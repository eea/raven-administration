"""Generate the AQR3 export section of swagger.json from the registry.

The checked-in swagger.json had drifted badly — it documented four
/api/dataflow/reportnet3/* paths that no longer existed and none of the CSV
endpoints that did. Deriving the paths from the registry means it cannot drift
again.

Regenerate after changing the registry:

    python -c "from core.reporting.aqr3.swagger import write_swagger; write_swagger()"
"""
import json
from pathlib import Path

from core.reporting.aqr3.spec import AQR3_TABLES

SWAGGER_PATH = Path(__file__).resolve().parents[3] / 'static' / 'swagger.json'

_OK = {'200': {'description': 'Successful operation'},
       '401': {'description': 'Missing or invalid token'},
       '403': {'description': 'Exporting claim required'}}


def aqr3_paths():
    """The /api/dataflow/csv/* paths implied by the registry."""
    codes = ', '.join(AQR3_TABLES)
    paths = {
        '/api/dataflow/csv/tables': {
            'get': {
                'summary': 'List the AQR3 v5.02 reporting tables',
                'description': 'Registry metadata: code, filename, description, '
                               'whether the table is reported per year, and its column headers.',
                'parameters': [],
                'responses': _OK,
            }
        },
        '/api/dataflow/csv/available_years': {
            'get': {
                'summary': 'Reporting years with sampling point activity',
                'parameters': [],
                'responses': _OK,
            }
        },
        '/api/dataflow/csv/download_all': {
            'post': {
                'summary': 'All AQR3 tables as a ZIP',
                'description': 'Empty tables are omitted. Without a year, the year-dependent '
                               'tables are omitted too. Both are listed in the X-AQR3-Skipped '
                               'response header.',
                'parameters': [{
                    'in': 'body', 'name': 'body', 'required': False,
                    'schema': {'type': 'object',
                               'properties': {'year': {'type': 'integer'}}},
                }],
                'responses': _OK,
            }
        },
        '/api/dataflow/csv/{table}': {
            'post': {
                'summary': 'One AQR3 reporting table as CSV',
                'description': f'`table` is an AQR3 table code ({codes}) or a legacy slug '
                               f'such as `stations`. Year-dependent tables require `year`.',
                'parameters': [
                    {'in': 'path', 'name': 'table', 'required': True, 'type': 'string'},
                    {'in': 'body', 'name': 'body', 'required': False,
                     'schema': {'type': 'object',
                                'properties': {'year': {'type': 'integer'}}}},
                ],
                'responses': {**_OK,
                              '400': {'description': 'Year required for a year-dependent table'},
                              '404': {'description': 'Unknown AQR3 table'}},
            }
        },
    }
    return paths


def write_swagger(path=SWAGGER_PATH):
    """Replace the dataflow section of swagger.json, keeping everything else."""
    doc = json.loads(Path(path).read_text(encoding='utf-8'))
    doc.setdefault('info', {})['version'] = 'AQR3 v5.02'
    doc['info']['title'] = 'RAVEN Reportnet3 (AQR3 v5.02) API'

    kept = {p: v for p, v in doc.get('paths', {}).items()
            if not p.startswith('/api/dataflow/')}
    doc['paths'] = {**kept, **aqr3_paths()}

    Path(path).write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
    return sorted(doc['paths'])
