"""Turn a TableSpec plus an ExportContext into CSV bytes."""
import csv
import zipfile
from io import BytesIO, StringIO

from core.database import CursorFromPool
from core.reporting.aqr3.context import build_context
from core.reporting.aqr3.spec import AQR3_TABLES


def _query_params(spec, ctx):
    """Only pass the parameters this spec's SQL actually references."""
    available = {'country_code': ctx.country_code, 'year': ctx.year}
    return {k: available[k] for k in spec.params}


def build_csv(spec, ctx, cursor):
    """Render one AQR3 table. Returns '' when there are no rows.

    An empty string rather than a header-only file: the ZIP builder skips empty
    tables, matching the previous behaviour, and Reportnet3 has no use for a file
    with no records.
    """
    if spec.year_dependent and ctx.year is None:
        raise ValueError(f'{spec.name} requires a reporting year')

    cursor.execute(spec.sql, _query_params(spec, ctx))
    rows = cursor.fetchall()
    if not rows:
        return ''

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=spec.headers(), quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for row in rows:
        writer.writerow({c.name: c.render(row, ctx) for c in spec.columns})
    return buffer.getvalue()


def build_csv_for(code_or_spec, year=None):
    """Convenience entry point: open a cursor, build the context, render."""
    spec = code_or_spec if hasattr(code_or_spec, 'columns') else AQR3_TABLES[code_or_spec]
    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)
        return build_csv(spec, ctx, cursor), spec.filename


def build_zip(year=None, codes=None):
    """Render every in-scope table into a ZIP, skipping the empty ones.

    Year-dependent tables are omitted when no year is supplied rather than
    failing the whole archive.
    """
    selected = [AQR3_TABLES[c] for c in codes] if codes else list(AQR3_TABLES.values())

    buffer = BytesIO()
    included, skipped = [], []
    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            for spec in selected:
                if spec.year_dependent and ctx.year is None:
                    skipped.append(f'{spec.filename} (no reporting year given)')
                    continue
                content = build_csv(spec, ctx, cursor)
                if content:
                    archive.writestr(spec.filename, content)
                    included.append(spec.filename)
                else:
                    skipped.append(f'{spec.filename} (no data)')

    buffer.seek(0)
    return buffer.read(), included, skipped
