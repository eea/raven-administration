"""Generic management-table CSV import.

Mirrors the export side:

  /api/imports/<table>      v1 — accepts the pre-AQR3 headers
  /api/v2/imports/<table>   v2 — accepts the AQR3 v5.02 aligned column names

See core/data/management.py (V1_ALIASES) for the translation.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

from core.data.management import Management
from core.database import CursorFromPool
from core.jwt_ext_custom import (
    jwt_required_with_allnetworks_claim,
    jwt_required_with_management_claim,
)

import_management_endpoint = Blueprint("import_management", __name__)

# table -> columns excluded from the generic round-trip
IMPORTABLE = {
    "authorities": [],
    "zones": [],
    "networks": [],
    "stations": [],
    # from_time/to_time are in the round-trip: from_time is the default AQR3
    # SPL_03 LocationBegin and part of the AQR3 key, and a country with hundreds
    # of sampling points needs a bulk way to set it.
    "sampling_points": [],
    "processes": [],
    "documents": [],
}


def _import(table, naming):
    if table not in IMPORTABLE:
        raise NotFound(f'Unknown management table "{table}". '
                       f'Available: {", ".join(sorted(IMPORTABLE))}')
    if "file" not in request.files:
        raise BadRequest("File form does not contain the key 'file'")

    with CursorFromPool() as cursor:
        m = Management(cursor, table, IMPORTABLE[table], naming=naming)
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/<table>", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_v1(table):
    """v1: legacy headers."""
    return _import(table, naming="v1")


@import_management_endpoint.route("/api/v2/imports/<table>", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_v2(table):
    """v2: AQR3 v5.02 column names."""
    return _import(table, naming="v2")
