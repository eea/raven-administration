#!/usr/bin/env python3
"""Apply pending SQL migrations from sql/migrations/ in filename order.

Raven has no alembic. sql/schema.sql is the fresh-install schema and
sql/migrations/NNN_*.sql carry the same changes for existing databases; both are
updated in the same commit. Each migration records itself in schema_version, and
every migration is written to be idempotent, so re-running is safe either way.

Migrations 001-010 were folded into sql/schema.sql at 4.502.11 and moved to
sql/migrations/archive/, which this script cannot see (see migration_files()).
sql/migrations/011_migration_baseline.sql is the only live one; it holds the
version slot so the next migration is 012, and it refuses to apply itself to a
database that predates the fold-in.

Usage:
    python sql/apply_migrations.py                 # apply pending
    python sql/apply_migrations.py --dry-run       # list pending, change nothing
    python sql/apply_migrations.py --baseline      # record pending as applied, run nothing
    python sql/apply_migrations.py --db-uri URI    # override $DB_URI
"""
import argparse
import os
import re
import sys
from pathlib import Path

import psycopg2

MIGRATIONS_DIR = Path(__file__).parent / 'migrations'
VERSION_RE = re.compile(r"insert\s+into\s+schema_version\s*\([^)]*\)\s*values\s*\(\s*'([^']+)'",
                        re.I | re.S)

# Arbitrary but fixed key, so every runner against a database contends on the
# same lock. Kubernetes starts one migrating pod per replica (raven-v4 runs two),
# and the migrations are idempotent but not concurrency-safe.
ADVISORY_LOCK_KEY = 4502_0001
LOCK_WAIT_SECONDS = 900


def migration_files():
    """Live migrations, in filename order.

    NON-recursive on purpose, and that is load-bearing. Migrations 001-010 were
    folded into sql/schema.sql and moved to sql/migrations/archive/; making this
    glob recursive would resurrect all ten against every database, re-running
    renames against a schema that already carries the new names.
    tests/unit/test_migration_layout.py asserts this returns exactly one file.
    """
    return sorted(MIGRATIONS_DIR.glob('*.sql'), key=lambda p: p.name)


def declared_version(sql_text, filename):
    m = VERSION_RE.search(sql_text)
    if not m:
        raise SystemExit(
            f"{filename}: no `insert into schema_version (...) values ('<version>', ...)` found. "
            f"Every migration must record its own version.")
    return m.group(1)


def acquire_advisory_lock(cursor):
    """Serialise concurrent runners. Session-scoped: released when the connection
    closes, including on crash, so a dead pod cannot wedge the next one.

    MUST be held before applied_versions() is read — otherwise a second runner
    computes its pending list from a schema_version the first has not committed
    yet, and re-applies migrations already in flight.
    """
    cursor.execute("SET lock_timeout = %s", (f'{LOCK_WAIT_SECONDS}s',))
    cursor.execute("SELECT pg_try_advisory_lock(%s)", (ADVISORY_LOCK_KEY,))
    if cursor.fetchone()[0]:
        return
    print(f'Another migration run holds the lock; waiting up to {LOCK_WAIT_SECONDS}s ...')
    try:
        cursor.execute("SELECT pg_advisory_lock(%s)", (ADVISORY_LOCK_KEY,))
    except psycopg2.errors.LockNotAvailable:
        raise SystemExit(
            f'Timed out after {LOCK_WAIT_SECONDS}s waiting for the migration lock. '
            f'Another runner is still working, or a connection is wedged holding '
            f'advisory lock {ADVISORY_LOCK_KEY}.')
    print('Lock acquired.')


def ensure_schema_version_table(cursor):
    """Defensive: schema.sql normally creates this. Definition must match it."""
    cursor.execute("""
        create table if not exists schema_version
        (
            version     varchar(20) not null primary key,
            description text,
            applied_at  timestamp default CURRENT_TIMESTAMP
        )
    """)


def applied_versions(cursor):
    cursor.execute("""
        SELECT EXISTS (SELECT 1 FROM information_schema.tables
                       WHERE table_name = 'schema_version')
    """)
    if not cursor.fetchone()[0]:
        return set()
    cursor.execute('SELECT version FROM schema_version')
    return {r[0] for r in cursor.fetchall()}


# psycopg2 opens a transaction before executing, and every migration file also
# carries its own `begin;`/`commit;`. PostgreSQL therefore emits these two on each
# file. They say nothing about whether the migration worked, so they are dropped
# rather than shown — otherwise every run ends with warnings the operator should
# ignore, which trains them to ignore the real ones.
_TRANSACTION_NOISE = (
    'there is already a transaction in progress',
    'there is no transaction in progress',
)


def _is_transaction_noise(line):
    lowered = line.lower()
    return any(noise in lowered for noise in _TRANSACTION_NOISE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-uri', default=os.getenv('DB_URI'))
    ap.add_argument('--dry-run', action='store_true',
                    help='list pending migrations and change nothing')
    ap.add_argument('--baseline', action='store_true',
                    help='record pending migrations as applied WITHOUT running them. '
                         'Only for a database whose schema already matches sql/schema.sql '
                         '(a fresh install predating the schema_version seed). On any other '
                         'database this permanently skips migrations that still need to run '
                         '-- including the fold-in guard in 011_migration_baseline.sql, which '
                         'exists to catch exactly that mistake. Verify the schema first.')
    args = ap.parse_args()

    if not args.db_uri:
        raise SystemExit('No database URI. Set DB_URI or pass --db-uri.')

    if args.dry_run and args.baseline:
        raise SystemExit('--dry-run and --baseline are mutually exclusive.')

    files = migration_files()
    if not files:
        print('No migrations found.')
        return 0

    conn = psycopg2.connect(args.db_uri)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # --dry-run only reads, so it must never block behind a real run.
            if not args.dry_run:
                acquire_advisory_lock(cur)
            if args.baseline:
                ensure_schema_version_table(cur)
            done = applied_versions(cur)

        if args.baseline:
            print(f'Already recorded: {", ".join(sorted(done)) if done else "(none)"}')

        pending = []
        for path in files:
            text = path.read_text(encoding='utf-8')
            version = declared_version(text, path.name)
            if version in done:
                print(f'  skip    {path.name}  ({version} already applied)')
            else:
                pending.append((path, version, text))

        if not pending:
            print('Database is up to date.')
            return 0

        if args.dry_run:
            print('\nPending:')
            for path, version, _ in pending:
                print(f'  {path.name}  -> {version}')
            return 0

        if args.baseline:
            # Record only. Migration bodies are never read beyond the version regex.
            print('\nRecording as applied WITHOUT running (--baseline):')
            for path, version, _ in pending:
                print(f'  baseline {path.name}  -> {version}')
                with conn.cursor() as cur:
                    cur.execute("""
                        insert into schema_version (version, description)
                        values (%s, %s)
                        on conflict (version) do nothing
                    """, (version, f'baseline: pre-satisfied by schema.sql ({path.name} not run)'))
            conn.commit()
            print(f'\nBaselined {len(pending)} migration(s). Nothing was executed.')
            return 0

        warned = False
        for path, version, text in pending:
            print(f'  apply   {path.name}  -> {version}')
            # Migrations use `raise notice` / `raise warning` to report what they
            # actually did and what the operator still has to do. Without this the
            # messages go nowhere — psycopg2 buffers them on the connection rather
            # than printing them, so they were invisible in the normal path and in
            # the Docker entrypoint.
            del conn.notices[:]
            with conn.cursor() as cur:
                # Each migration file manages its own begin/commit.
                cur.execute(text)
            conn.commit()
            for notice in conn.notices:
                line = notice.strip()
                if not line or _is_transaction_noise(line):
                    continue
                print(f'          {line}')
                if line.upper().startswith('WARNING'):
                    warned = True

        print(f'\nApplied {len(pending)} migration(s).')
        if warned:
            print('Some migrations raised warnings — read them above before reporting.')
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
