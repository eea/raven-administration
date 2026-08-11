#!/usr/bin/env python3
"""Apply pending SQL migrations from sql/migrations/ in filename order.

Raven has no alembic. sql/schema.sql is the fresh-install schema and
sql/migrations/NNN_*.sql carry the same changes for existing databases; both are
updated in the same commit. Each migration records itself in schema_version, and
every migration is written to be idempotent, so re-running is safe either way.

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


def migration_files():
    return sorted(MIGRATIONS_DIR.glob('*.sql'), key=lambda p: p.name)


def declared_version(sql_text, filename):
    m = VERSION_RE.search(sql_text)
    if not m:
        raise SystemExit(
            f"{filename}: no `insert into schema_version (...) values ('<version>', ...)` found. "
            f"Every migration must record its own version.")
    return m.group(1)


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db-uri', default=os.getenv('DB_URI'))
    ap.add_argument('--dry-run', action='store_true',
                    help='list pending migrations and change nothing')
    ap.add_argument('--baseline', action='store_true',
                    help='record pending migrations as applied WITHOUT running them. '
                         'Only for a database whose schema already matches sql/schema.sql '
                         '(a fresh install predating the schema_version seed). On any other '
                         'database this permanently skips migrations that still need to run.')
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

        for path, version, text in pending:
            print(f'  apply   {path.name}  -> {version}')
            with conn.cursor() as cur:
                # Each migration file manages its own begin/commit.
                cur.execute(text)
            conn.commit()

        print(f'\nApplied {len(pending)} migration(s).')
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    sys.exit(main())
