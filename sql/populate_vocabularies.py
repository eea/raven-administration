#!/usr/bin/env python3
"""Load the EEA vocabularies that AQR3 v5.02 reporting depends on.

Run as the last step of a fresh install:

    psql < sql/schema.sql
    psql < sql/data.sql
    python sql/apply_migrations.py
    python sql/populate_vocabularies.py          # <- this

Usage:
    python sql/populate_vocabularies.py
    python sql/populate_vocabularies.py --dry-run
    python sql/populate_vocabularies.py --tables eea_countries,eea_objectivetypes
    python sql/populate_vocabularies.py --offline          # curated fallbacks only
    python sql/populate_vocabularies.py --db-uri postgresql://...

Exit code is **non-zero** if any in-scope table ends up empty or on a fallback, so
a silent total failure cannot look like success. dd.eionet is genuinely unreliable
— several vocabularies return HTTP 500 and it rate-limits — so that distinction
matters more here than usual.

The registry lives in sql/vocabularies.py.
"""
import argparse
import csv
import io
import os
import sys
import xml.etree.ElementTree as ET


import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vocabularies import (  # noqa: E402
    OUT_OF_SCOPE,
    TIMESTEP_SECONDS,
    VOCABULARIES,
)

SKOS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
}
ABOUT = f'{{{SKOS["rdf"]}}}about'
LANG = '{http://www.w3.org/XML/1998/namespace}lang'

# Outcome of *this run's* fetch for a table — distinct from how many rows the
# table ends up holding, which may be non-zero from data.sql even when the fetch
# produced nothing.
FETCHED, FALLBACK, EMPTY, SKIPPED = 'fetched', 'fallback', 'no-source', 'skipped'


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def build_session(retries, timeout):
    """A session that retries on the failures dd.eionet actually produces.

    It rate-limits under sustained polling and intermittently 500s, so retry on
    429/500/502/503/504 with backoff and send a real User-Agent.
    """
    import requests
    from requests.adapters import HTTPAdapter

    try:
        from urllib3.util.retry import Retry
    except ImportError:                                   # very old urllib3
        from requests.packages.urllib3.util.retry import Retry

    retry = Retry(
        total=retries,
        backoff_factor=1.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(['GET']),
        raise_on_status=False,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers['User-Agent'] = (
        'raven-admin/5.0 (+https://github.com/eea/raven-administration) '
        'AQR3 vocabulary loader'
    )
    session.request_timeout = timeout
    return session


def parse_skos(content):
    """Extract concepts from a SKOS RDF/XML document.

    More forgiving than a plain notation+prefLabel lookup:
      * searches descendants, since concept nesting varies between vocabularies
      * prefers the English prefLabel when several languages are present
      * falls back to the last URI segment when skos:notation is absent, rather
        than dropping the concept silently

    Deprecated concepts are *not* filtered: the EEA Data Dictionary marks status
    with a non-SKOS property whose shape I could not confirm (dd.eionet was
    unreachable), and guessing at it risks dropping live concepts. Worth revisiting
    against a real payload — reporting a retired code is a QC failure.
    """
    root = ET.fromstring(content)
    concepts = []

    for concept in root.findall(f'.//{{{SKOS["skos"]}}}Concept'):
        uri = concept.get(ABOUT, '') or ''

        labels = concept.findall(f'.//{{{SKOS["skos"]}}}prefLabel')
        label = ''
        for el in labels:
            if (el.get(LANG) or '').lower().startswith('en'):
                label = (el.text or '').strip()
                break
        if not label and labels:
            label = (labels[0].text or '').strip()

        notation_el = concept.find(f'.//{{{SKOS["skos"]}}}notation')
        notation = (notation_el.text or '').strip() if notation_el is not None else ''
        if not notation and uri:
            notation = uri.rstrip('/').rsplit('/', 1)[-1]

        # A concept with no usable key is unusable.
        if not (notation or uri):
            continue

        concepts.append({
            'uri': uri,
            'notation': notation,
            'label': label or notation,
        })

    return concepts


def parse_csv(content):
    """Extract concepts from a Data Dictionary CSV export.

    The header has duplicate column names, so DictReader is unusable; read
    positionally and locate the columns by name instead of hardcoding indices
    (the pre-existing loader hardcoded 19 positions and silently corrupts if EEA
    reorders a column).
    """
    reader = csv.reader(io.StringIO(content))
    try:
        header = next(reader)
    except StopIteration:
        return []

    lowered = [h.strip().lower() for h in header]

    def col(*names):
        for name in names:
            if name in lowered:
                return lowered.index(name)
        return None

    i_uri = col('uri')
    i_label = col('label', 'preflabel')
    i_notation = col('notation')

    concepts = []
    for row in reader:
        if not row:
            continue

        def get(idx):
            return row[idx].strip() if idx is not None and idx < len(row) else ''

        uri, notation, label = get(i_uri), get(i_notation), get(i_label)
        if not notation and uri:
            notation = uri.rstrip('/').rsplit('/', 1)[-1]
        if not (notation or uri):
            continue
        concepts.append({'uri': uri, 'notation': notation, 'label': label or notation})

    return concepts


def fetch(session, vocab, log):
    """Try each candidate URL in order. Returns (concepts, source_url) or ([], None)."""
    parse = parse_csv if vocab.fmt == 'csv' else parse_skos

    for url in vocab.urls():
        try:
            response = session.get(url, timeout=session.request_timeout)
        except Exception as e:                            # network/DNS/timeout
            log(f'      {url} -> {type(e).__name__}')
            continue

        if response.status_code != 200:
            log(f'      {url} -> HTTP {response.status_code}')
            continue

        try:
            body = response.text if vocab.fmt == 'csv' else response.content
            concepts = parse(body)
        except Exception as e:
            log(f'      {url} -> unparseable ({type(e).__name__}: {e})')
            continue

        if concepts:
            return concepts, url
        log(f'      {url} -> 200 but no concepts parsed')

    return [], None


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------

def column_widths(cursor, table):
    """{column: max_length|None} so labels are trimmed to the real column width.

    The pre-existing loader truncated every label to 100 characters regardless,
    needlessly shortening eea_analyticaltechnique (150), eea_datatable and
    eea_documentobject (255) and eea_aggregationprocess (text) — and blowing up on
    eea_documentobject.id (50).
    """
    cursor.execute("""
        SELECT column_name, character_maximum_length, data_type
        FROM information_schema.columns
        WHERE table_name = %s
    """, (table,))
    return {r[0]: (r[1], r[2]) for r in cursor.fetchall()}


def clip(value, spec):
    """Trim to the column's declared width; leave everything else untouched.

    Only character columns have a maximum length, so anything else is passed
    through as-is — stringifying would turn an integer id such as the validity
    code -99 into '-99'.
    """
    if value is None or spec is None:
        return value
    max_len, _ = spec
    if not max_len:
        return value
    return str(value)[:max_len]


def derive_id(concept, id_from):
    """Apply the vocabulary's id convention. Returns None when unusable."""
    # Fallback rows carry an explicit id (validity codes are negative integers,
    # which no derivation strategy would produce).
    if concept.get('_id') is not None:
        return concept['_id']

    uri = concept.get('uri') or ''
    suffix = uri.rstrip('/').rsplit('/', 1)[-1] if uri else ''

    if id_from == 'uri_suffix':
        return suffix or None
    if id_from == 'numeric_uri_suffix':
        try:
            return int(suffix)
        except (TypeError, ValueError):
            return None
    return concept.get('notation') or suffix or None


def upsert(cursor, table, concepts, id_from, widths, extra_timestep=False,
           notation_from='notation'):
    """Insert or refresh rows. Returns (written, rejected).

    Upserts with DO UPDATE rather than DO NOTHING so a corrected label upstream
    actually propagates — the pre-existing loader could only ever grow a table.

    notation_from='label' stores the label as the notation, for a vocabulary that
    supplies no notation of its own. Applied here rather than in parse_rdf/parse_csv
    because those are deliberately vocabulary-agnostic, and because derive_id must
    keep reading the real URI suffix (meteoparameter ids have to stay 51-99).
    """
    written, rejected = 0, []
    has_notation = 'notation' in widths
    has_uri = 'uri' in widths

    for n, concept in enumerate(concepts):
        row_id = derive_id(concept, id_from)
        if row_id is None:
            rejected.append(concept.get('uri') or concept.get('notation') or '?')
            continue

        cols = ['id', 'label']
        vals = [clip(row_id, widths.get('id')), clip(concept['label'], widths.get('label'))]
        if has_notation:
            notation = concept['label'] if notation_from == 'label' else concept['notation']
            cols.append('notation')
            vals.append(clip(notation, widths.get('notation')))
        if has_uri:
            cols.append('uri')
            vals.append(clip(concept['uri'], widths.get('uri')))
        if extra_timestep:
            cols.append('timestep')
            vals.append(TIMESTEP_SECONDS.get(concept['notation'], 1))

        updates = ', '.join(f'{c} = EXCLUDED.{c}' for c in cols if c != 'id')
        sql = (f'INSERT INTO {table} ({", ".join(cols)}) '
               f'VALUES ({", ".join(["%s"] * len(cols))}) '
               f'ON CONFLICT (id) DO UPDATE SET {updates}')

        # A savepoint per row, so one bad concept does not discard the whole load.
        # A bare rollback() here would undo every table done so far — the bug the
        # older populate_lookups.py shipped with.
        savepoint = f'row_{n}'
        cursor.execute(f'SAVEPOINT {savepoint}')
        try:
            cursor.execute(sql, vals)
            cursor.execute(f'RELEASE SAVEPOINT {savepoint}')
            written += 1
        except Exception as e:
            cursor.execute(f'ROLLBACK TO SAVEPOINT {savepoint}')
            rejected.append(f'{row_id} ({str(e).splitlines()[0][:70]})')

    return written, rejected


def fallback_concepts(vocab):
    """Fallback rows, with a URI synthesised from the vocabulary path."""
    from vocabularies import DD_BASE
    out = []
    for row in vocab.fallback:
        out.append({
            'uri': f'{DD_BASE}/{vocab.path}/{row["notation"]}',
            'notation': row['notation'],
            'label': row['label'],
            '_id': row['id'],
        })
    return out


def row_count(cursor, table):
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    return cursor.fetchone()[0]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--db-uri', default=os.getenv('DB_URI'))
    ap.add_argument('--tables', help='comma-separated subset of eea_* tables')
    ap.add_argument('--dry-run', action='store_true', help='fetch and report, write nothing')
    ap.add_argument('--offline', action='store_true', help='use curated fallbacks only')
    ap.add_argument('--timeout', type=int, default=45)
    ap.add_argument('--retries', type=int, default=3)
    ap.add_argument('--verbose', '-v', action='store_true', help='log every URL attempt')
    args = ap.parse_args()

    if not args.db_uri:
        raise SystemExit('No database URI. Set DB_URI or pass --db-uri.')

    wanted = {t.strip() for t in args.tables.split(',')} if args.tables else None
    selected = [v for v in VOCABULARIES if wanted is None or v.table in wanted]
    if wanted:
        unknown = wanted - {v.table for v in VOCABULARIES}
        if unknown:
            raise SystemExit(f'Unknown table(s): {", ".join(sorted(unknown))}')

    def log(msg):
        if args.verbose:
            print(msg)

    session = None if args.offline else build_session(args.retries, args.timeout)

    conn = psycopg2.connect(args.db_uri)
    conn.autocommit = False

    # table -> {'status', 'written', 'source', 'note', 'rejected'}
    results = {}
    aqr3_of = {}

    try:
        with conn.cursor() as cursor:
            existing = {r[0] for r in _existing_tables(cursor)}

            for vocab in selected:
                if vocab.table not in existing:
                    results.setdefault(vocab.table, {})['status'] = SKIPPED
                    results[vocab.table]['note'] = 'table does not exist in this database'
                    continue

                aqr3_of.setdefault(vocab.table, []).append(vocab.aqr3 or '-')
                print(f'  {vocab.table:38} {vocab.path}')

                concepts, source = ([], None) if args.offline else fetch(session, vocab, log)
                status = FETCHED
                note = ''

                if not concepts:
                    if not vocab.fallback:
                        prev = results.get(vocab.table, {})
                        if prev.get('status') == FETCHED:
                            continue          # another source already filled it
                        results[vocab.table] = {
                            'status': EMPTY, 'written': 0, 'source': None,
                            'note': ('not attempted (--offline) and no fallback defined'
                                     if args.offline else
                                     'unreachable and no fallback defined'),
                            'rejected': [],
                        }
                        print('      -> nothing fetched, no fallback')
                        continue
                    concepts = fallback_concepts(vocab)
                    status = FALLBACK
                    note = vocab.fallback_note
                    print(f'      -> FALLBACK ({len(concepts)} rows): {note}')

                widths = column_widths(cursor, vocab.table)
                targets = [vocab.table, *vocab.also_into]

                total = 0
                rejected = []
                for target in targets:
                    if target not in existing:
                        continue
                    t_widths = widths if target == vocab.table else column_widths(cursor, target)
                    written, rej = upsert(cursor, target, concepts, vocab.id_from, t_widths,
                                         extra_timestep=(vocab.table == 'eea_times'),
                                         notation_from=vocab.notation_from)
                    total += written
                    rejected.extend(rej)

                prev = results.get(vocab.table)
                if prev and prev.get('status') == FETCHED and status == FALLBACK:
                    continue                  # do not downgrade a successful source
                results[vocab.table] = {
                    'status': status, 'written': total, 'source': source,
                    'note': note, 'rejected': rejected,
                }
                print(f'      -> {total} row(s)'
                      + (f', {len(rejected)} rejected' if rejected else ''))

            if args.dry_run:
                conn.rollback()
                print('\n[dry run] rolled back — nothing was written')
            else:
                conn.commit()

            with conn.cursor() as c2:
                counts = {t: row_count(c2, t) for t in sorted(results) if t in existing}
    finally:
        conn.close()

    return report(results, counts, aqr3_of, args)


def _existing_tables(cursor):
    cursor.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name LIKE 'eea_%'
    """)
    return cursor.fetchall()


def report(results, counts, aqr3_of, args):
    """Print the summary and decide the exit code."""
    print()
    print('=' * 96)
    print('  status = this run\'s fetch outcome;  rows = the table\'s row count afterwards')
    print('  (a table can show "no-source" and still have rows, if data.sql already seeded it)')
    print('=' * 96)
    print(f'{"table":38} {"status":9} {"rows":>6}  AQR3 attribute')
    print('-' * 96)

    fetched = fallbacks = empties = skips = 0
    for table in sorted(results):
        r = results[table]
        status = r.get('status')
        rows = counts.get(table, 0)
        attrs = '; '.join(a for a in aqr3_of.get(table, []) if a and a != '-') or '-'
        print(f'  {table:36} {status:9} {rows:>6}  {attrs[:44]}')
        if r.get('note'):
            print(f'  {"":36} {"":9} {"":>6}  ! {r["note"][:80]}')
        for bad in r.get('rejected', [])[:3]:
            print(f'  {"":36} {"":9} {"":>6}  rejected: {bad}')

        if status == FETCHED and rows:
            fetched += 1
        elif status == FALLBACK:
            fallbacks += 1
        elif status == SKIPPED:
            skips += 1
        else:
            empties += 1

    empty_now = [t for t, n in counts.items() if n == 0]
    print('-' * 96)
    print(f'  fetched from EEA: {fetched}   fallback: {fallbacks}   '
          f'empty: {len(empty_now)}   skipped: {skips}')

    if args.dry_run:
        print('\n[dry run] no changes were written')
        return 0

    problems = []
    if empty_now:
        problems.append(f'{len(empty_now)} table(s) still empty: {", ".join(sorted(empty_now))}')
    if fallbacks:
        problems.append(f'{fallbacks} table(s) loaded from curated fallbacks rather than EEA')

    if problems:
        print()
        for p in problems:
            print(f'  WARNING: {p}')
        print('\n  Re-run when dd.eionet is reachable. Vocabularies deliberately not handled '
              'here:')
        for path, why in sorted(OUT_OF_SCOPE.items()):
            print(f'    {path:34} {why}')
        print('\n  Reminder: settings.country_code_id must be set — CountryCode is the first '
              'column of every AQR3 table.')
        return 1

    print('\n  All in-scope vocabularies loaded from the EEA Data Dictionary.')
    print('  Reminder: settings.country_code_id must be set — CountryCode is the first '
          'column of every AQR3 table.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
