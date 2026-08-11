#!/usr/bin/env python3
"""Apply pending SQL migrations from sql/migrations/ in filename order.

Raven has no alembic. sql/schema.sql is the fresh-install schema and
sql/migrations/NNN_*.sql carry the same changes for existing databases; both are
updated in the same commit. Each migration records itself in schema_version, and
every migration is written to be idempotent, so re-running is safe either way.

Usage:
    python sql/apply_migrations.py                 # apply pending
    python sql/apply_migrations.py --dry-run       # list pending, change nothing
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
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    if not args.db_uri:
        raise SystemExit('No database URI. Set DB_URI or pass --db-uri.')

    files = migration_files()
    if not files:
        print('No migrations found.')
        return 0

    conn = psycopg2.connect(args.db_uri)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            done = applied_versions(cur)

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
