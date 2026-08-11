"""AQR3 v5.02 Reportnet3 CSV export endpoints.

Every table is served by the same two handlers, driven by the registry in
core/reporting/aqr3/spec.py — adding a reporting table needs no change here.
"""
from datetime import datetime

from flask import Blueprint, Response, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_exporting_claim
from core.reporting.aqr3 import AQR3_TABLES, build_csv, build_context, build_zip, resolve
from core.reporting.aqr3.compliance import persist_compliance
from core.utils import U

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

    Empty tables and — when no year is given — the year-dependent ones are left
    out, and what was left out is reported in a header so the omission is visible
    rather than silent.
    """
    year = _requested_year()
    payload, included, skipped = build_zip(year)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = Response(payload, mimetype='application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename=aqr3_export_{timestamp}.zip'
    response.headers['X-AQR3-Included'] = ','.join(included)
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

    with CursorFromPool() as cursor:
        ctx = build_context(cursor, year)
        content = build_csv(spec, ctx, cursor)

    filename = (f'{spec.name}_{year}.csv' if spec.year_dependent else spec.filename)
    return U.csv_response(content, filename)
