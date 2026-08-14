"""AQR3 v5.02 Reportnet3 CSV export endpoints.

Every table is served by the same two handlers, driven by the registry in
core/reporting/aqr3/spec.py — adding a reporting table needs no change here.
"""
from datetime import datetime

from flask import Blueprint, Response, jsonify, request, stream_with_context
from werkzeug.exceptions import BadRequest, NotFound

from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_exporting_claim
from core.reporting.aqr3 import AQR3_TABLES, build_context, build_zip, resolve
from core.reporting.aqr3.compliance import persist_compliance
from core.reporting.aqr3.writer import primed, stream_csv

dataflow_endpoint = Blueprint('dataflow', __name__)


def _requested_year():
    """Reporting year from the JSON body, if present."""
    data = request.get_json(silent=True) or {}
    year = data.get('year')
    if year in (None, ''):
        return None
    try:
        return int(year)
    except (TypeError, ValueError):
        raise BadRequest('Year must be a valid integer')


@dataflow_endpoint.route('/api/dataflow/csv/tables', methods=['GET'])
@jwt_required_with_exporting_claim()
def list_tables():
    """The registry, so the client renders the export list from one source."""
    return jsonify([
        {
            'code': spec.code,
            'name': spec.name,
            'filename': spec.filename,
            'description': spec.description,
            'year_dependent': spec.year_dependent,
            'columns': spec.headers(),
        }
        for spec in AQR3_TABLES.values()
    ])


@dataflow_endpoint.route('/api/dataflow/csv/available_years', methods=['GET'])
@jwt_required_with_exporting_claim()
def get_available_years():
    """Years for which sampling points were active."""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT DISTINCT EXTRACT(YEAR FROM year_date)::integer as year
            FROM (
                SELECT from_time as year_date FROM sampling_points WHERE from_time IS NOT NULL
                UNION
                SELECT to_time as year_date FROM sampling_points WHERE to_time IS NOT NULL
            ) years
            ORDER BY year DESC
        """)
        return jsonify([row['year'] for row in cursor.fetchall()])


@dataflow_endpoint.route('/api/dataflow/csv/download_all', methods=['POST'])
@jwt_required_with_exporting_claim()
def export_all_csv():
    """Every in-scope table as a ZIP.

    Tables with no rows are included as a header-only file; only the
    year-dependent ones are left out, and only when no year was given. Which
    files are empty and which were omitted come back in headers so the export
    page can say so rather than leaving it to be discovered file by file.
    """
    year = _requested_year()
    payload, included, skipped, empty = build_zip(year)

    def stream():
        """The archive spools to disk, so send it back in chunks and close it."""
        try:
            while True:
                block = payload.read(64 * 1024)
                if not block:
                    return
                yield block
        finally:
            payload.close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = Response(stream_with_context(stream()), mimetype='application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename=aqr3_export_{timestamp}.zip'
    response.headers['X-AQR3-Included'] = ','.join(included)
    # Included but header-only. Every table is now exported, so without this the
    # page cannot tell a table with nothing to report from one full of data.
    response.headers['X-AQR3-Empty'] = ','.join(empty)
    if skipped:
        response.headers['X-AQR3-Skipped'] = '; '.join(skipped)
    return response


@dataflow_endpoint.route('/api/dataflow/compliance/recalculate', methods=['POST'])
@jwt_required_with_exporting_claim()
def recalculate_compliance():
    """Recompute and store the compliance results that CAM reports.

    CAM is the only reporting table whose contents are derived rather than
    entered, so it has to be refreshed before export. Replaces the given year.
    """
    year = _requested_year()
    if year is None:
        raise BadRequest('A "year" is required to recalculate compliance')

    data = request.get_json(silent=True) or {}
    with CursorFromPool() as cursor:
        summary = persist_compliance(
            cursor,
            reporting_year=year,
            directive=data.get('directive'),
            pollutants=data.get('pollutants'),
            zones=data.get('zones'),
        )
    return jsonify(summary)


@dataflow_endpoint.route('/api/dataflow/csv/<table>', methods=['POST'])
@jwt_required_with_exporting_claim()
def export_table_csv(table):
    """One AQR3 table, by code (`STA`) or legacy slug (`stations`)."""
    spec = resolve(table)
    if spec is None:
        raise NotFound(f'Unknown AQR3 table "{table}". '
                       f'Known codes: {", ".join(AQR3_TABLES)}')

    year = _requested_year()
    if spec.year_dependent and year is None:
        raise BadRequest(f'{spec.name} is reported per year — a "year" is required')

    filename = (f'{spec.name}_{year}.csv' if spec.year_dependent else spec.filename)

    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)

    # Compress only when the client said it can decode it; a plain script that
    # does not would otherwise save gzip bytes into a .csv. Every browser sends
    # this, so the download path always gets the compressed version.
    gzipped = bool(request.accept_encodings['gzip'])

    # Streamed, not built in memory: ObservationMeasurementResult is millions of
    # rows for a reporting year, and materialising it OOM-killed the worker —
    # which reached the browser as a 502. Compressed because nothing else does it
    # (Traefik routes /api straight to the pod, bypassing the client's nginx) and
    # a full year is ~330 MB of CSV. `primed` draws the first chunk here so a
    # query error is still a clean 500 rather than a truncated 200.
    response = Response(
        stream_with_context(primed(stream_csv(spec, ctx, gzipped=gzipped))),
        mimetype='text/csv',
    )
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    if gzipped:
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
    return response
