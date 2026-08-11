"""Generic management-table CSV export.

Two API versions over the same tables:

  /api/exports/<table>      v1 — the pre-AQR3 headers, frozen for existing callers
  /api/v2/exports/<table>   v2 — the AQR3 v5.02 aligned column names

Management derives its headers from information_schema, so the AQR3 rename would
otherwise have changed every one of these contracts silently. The translation
lives in core/data/management.py (V1_ALIASES).

The seven per-table handlers this replaced were identical apart from the table
name; the named routes are kept as thin aliases so existing URLs keep working.
"""
from flask import Blueprint
from werkzeug.exceptions import NotFound

from core.data.management import Management
from core.database import CursorFromPool
from core.jwt_ext_custom import (
    jwt_required_with_allnetworks_claim,
    jwt_required_with_management_claim,
)
from core.utils import U

export_management_endpoint = Blueprint("export_management", __name__)

# table -> columns excluded from the generic round-trip
EXPORTABLE = {
    "authorities": [],
    "zones": [],
    "networks": [],
    "stations": [],
    "sampling_points": ["from_time", "to_time"],
    "processes": [],
    "documents": [],
}


def _export(table, naming):
    if table not in EXPORTABLE:
        raise NotFound(f'Unknown management table "{table}". '
                       f'Available: {", ".join(sorted(EXPORTABLE))}')
    with CursorFromPool() as cursor:
        m = Management(cursor, table, EXPORTABLE[table], naming=naming)
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, f"{table}.csv")


@export_management_endpoint.route("/api/exports/<table>", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_v1(table):
    """v1: legacy headers (e.g. stations.eoi_code, authorities.organisation_name)."""
    return _export(table, naming="v1")


@export_management_endpoint.route("/api/v2/exports/<table>", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_v2(table):
    """v2: AQR3 v5.02 column names (station_eoi_code, authority_name, ...)."""
    return _export(table, naming="v2")
