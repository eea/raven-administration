from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.data.management import Management
from core.jwt_ext_custom import (
    jwt_required_with_allnetworks_claim,
    jwt_required_with_management_claim,
)
import pandas as pd
import json
import ast

import_management_endpoint = Blueprint("import_management", __name__)


@import_management_endpoint.route("/api/imports/authorities", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "responsible_authorities")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/zones", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_test():
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


@import_management_endpoint.route(
    "/api/imports/observing_capabilities", methods=["POST"]
)
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_observing_capabilities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "observing_capabilities")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/samples", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_samples():
    with CursorFromPool() as cursor:
        m = Management(cursor, "samples")
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


@import_management_endpoint.route("/api/imports/attainments", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_attainments():
    with CursorFromPool() as cursor:
        m = Management(cursor, "attainments")
        m.parse_file(request.files["file"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/assessmentregime", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_assessmentregime():
    # Expecting two files
    with CursorFromPool() as cursor:
        m = Management(cursor, "assessmentregimes")
        m.parse_file(request.files["file1"])

        md = Management(cursor, "assessmentdata")
        md.parse_file(request.files["file2"])

        # col_lst = m.df.assessmentdata.values.tolist()
        # lst = [item for sublist in col_lst for item in ast.literal_eval(sublist)]
        # md = Management(cursor, "assessmentdata")
        # md.parse_list(lst)

        m.generic_insert()
        md.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route("/api/imports/exceedances", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_exceedances():
    with CursorFromPool() as cursor:
        m = Management(cursor, "exceedancedescriptions")
        m.parse_file(request.files["file"])

        col_lst = m.df.exceedingmethods.values.tolist()
        lst = [item for sublist in col_lst for item in ast.literal_eval(sublist)]
        md = Management(cursor, "exceedingmethods")
        md.parse_list(lst)

        m.generic_insert()
        md.generic_insert()
        return jsonify({"success": True})
