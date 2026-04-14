from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.data.management import Management
from core.jwt_ext_custom import (
    jwt_required_with_allnetworks_claim,
    jwt_required_with_management_claim,
)

import_management_endpoint = Blueprint("import_management", __name__)


@import_management_endpoint.route("/api/imports/authorities", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "authorities")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/zones", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_zones():
    with CursorFromPool() as cursor:
        m = Management(cursor, "zones")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/networks", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/stations", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/sampling_points", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/processes", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/documents", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_documents():
    with CursorFromPool() as cursor:
        m = Management(cursor, "documents")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})