"""Turn a TableSpec plus an ExportContext into CSV bytes.

Everything renders through `iter_csv`, which yields the file in chunks and never
holds more than one batch of rows. The AQR3 ObservationMeasurementResult table is
one row per measurement per sampling point per hour — millions of rows for a
reporting year — and building that in memory cost ~2.2 kB of RSS per row, which
OOM-killed the API pod and surfaced as a 502. Nothing here may accumulate the
whole table again.
"""
import csv
import zipfile
import zlib
from io import StringIO
from itertools import count
from tempfile import SpooledTemporaryFile

from core.database import CursorFromPool, NamedCursorFromPool
from core.reporting.aqr3.context import build_context
from core.reporting.aqr3.spec import AQR3_TABLES

# Rows rendered per yielded chunk. Large enough that per-chunk overhead is
# irrelevant, small enough that the buffer stays trivial next to the ~93 MB
# baseline of a worker.
BATCH_ROWS = 5000

# Beyond this a ZIP is written to a temp file instead of staying in RAM.
_ZIP_SPOOL_BYTES = 32 * 1024 * 1024

# Cursor names are scoped to their connection, and every export here holds its
# own, so a plain counter is enough to keep them readable in pg_stat_activity.
_cursor_seq = count(1)


def _query_params(spec, ctx):
    """Only pass the parameters this spec's SQL actually references."""
    available = {'country_code': ctx.country_code, 'year': ctx.year}
    return {k: available[k] for k in spec.params}


def iter_csv(spec, ctx, cursor):
    """Yield one AQR3 table as CSV text, a batch of rows at a time.

    The header is always emitted, including for a table with no rows: a
    header-only file says "this table was considered and is empty", where a
    zero-byte file is indistinguishable from an export that failed.
    """
    if spec.year_dependent and ctx.year is None:
        raise ValueError(f'{spec.name} requires a reporting year')

    cursor.execute(spec.sql, _query_params(spec, ctx))

    fieldnames = spec.headers()
    columns = spec.columns

    header = StringIO()
    csv.DictWriter(header, fieldnames=fieldnames, quoting=csv.QUOTE_ALL).writeheader()
    yield header.getvalue()

    while True:
        rows = cursor.fetchmany(BATCH_ROWS)
        if not rows:
            return

        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        for row in rows:
            writer.writerow({c.name: c.render(row, ctx) for c in columns})
        yield buffer.getvalue()


def build_csv(spec, ctx, cursor):
    """Render one AQR3 table to a single string — the header row at minimum.

    Kept for the tests; it materialises the whole table, so do not use it for a
    response — routes stream via `stream_csv`.
    """
    return ''.join(iter_csv(spec, ctx, cursor))


def stream_csv(spec, ctx, gzipped=True):
    """Yield one AQR3 table for an HTTP response, holding no more than a batch.

    Owns its database connection: the generator outlives the request handler, so
    the connection is opened here and returned by the context manager on the way
    out — including when the client disconnects part-way and the generator is
    closed early, which surfaces as GeneratorExit at the yield.

    Takes an already-built context rather than a year, so a misconfigured
    `settings` fails in the route with a normal 500 instead of half-way through a
    response whose headers have already been sent.

    With `gzipped`, chunks come back deflate-compressed with a gzip wrapper; the
    caller must then set `Content-Encoding: gzip`. Nothing compresses these
    responses otherwise — Traefik routes /api straight to the pod, so the client's
    nginx is not in the path — and a full reporting year is a ~330 MB download.
    """
    compressor = zlib.compressobj(6, zlib.DEFLATED, 31) if gzipped else None

    cursor_name = f'aqr3_{spec.code.lower()}_{next(_cursor_seq)}'
    with NamedCursorFromPool(cursor_name, itersize=BATCH_ROWS) as cursor:
        for chunk in iter_csv(spec, ctx, cursor):
            data = chunk.encode('utf-8')
            yield compressor.compress(data) if compressor else data
        if compressor:
            yield compressor.flush()


def primed(generator):
    """Pull the first chunk eagerly, keeping errors on the pre-response side.

    A streamed response commits its status and headers as soon as the first byte
    is yielded, so a failing query would otherwise reach the client as a
    truncated 200. Drawing one chunk here means SQL and context errors still
    raise inside the route and become a normal 500.
    """
    try:
        first = next(generator)
    except StopIteration:
        return iter(())

    def chained():
        yield first
        yield from generator

    return chained()


def build_csv_for(code_or_spec, year=None):
    """Convenience entry point: open a cursor, build the context, render."""
    spec = code_or_spec if hasattr(code_or_spec, 'columns') else AQR3_TABLES[code_or_spec]
    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)
        return build_csv(spec, ctx, cursor), spec.filename


def build_zip(year=None, codes=None):
    """Render every in-scope table into a ZIP.

    Tables with no rows are included as a header-only file rather than dropped —
    the archive is then a complete statement of the reporting year, and a missing
    file means something went wrong rather than "nothing to report". The only
    omission left is a year-dependent table when no year was supplied, whose SQL
    cannot be parameterised at all; that is reported in `skipped`.

    Returns (file object positioned at 0, included, skipped, empty), where
    `empty` are the included files that carry only a header — reported so the
    export page can say which tables had nothing, rather than leaving it to be
    discovered by opening 17 files. The file spools to disk past
    `_ZIP_SPOOL_BYTES` so a full-year archive never sits on the heap; the caller
    is responsible for closing it.
    """
    selected = [AQR3_TABLES[c] for c in codes] if codes else list(AQR3_TABLES.values())

    payload = SpooledTemporaryFile(max_size=_ZIP_SPOOL_BYTES, suffix='.zip')
    included, skipped, empty = [], [], []

    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)

    with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as archive:
        for spec in selected:
            if spec.year_dependent and ctx.year is None:
                skipped.append(f'{spec.filename} (no reporting year given)')
                continue

            cursor_name = f'aqr3_zip_{spec.code.lower()}_{next(_cursor_seq)}'
            with NamedCursorFromPool(cursor_name, itersize=BATCH_ROWS) as cursor:
                has_rows = False
                with archive.open(spec.filename, 'w') as member:
                    # iter_csv yields the header first, so anything after it is
                    # data — cheaper than counting rows a second time.
                    for position, chunk in enumerate(iter_csv(spec, ctx, cursor)):
                        if position:
                            has_rows = True
                        member.write(chunk.encode('utf-8'))
                included.append(spec.filename)
                if not has_rows:
                    empty.append(spec.filename)

    payload.seek(0)
    return payload, included, skipped, empty
