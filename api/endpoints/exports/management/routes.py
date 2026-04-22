import csv
import io
from flask import jsonify, Blueprint, request, Response
from core.database import CursorFromPool
from core.data.management import Management
from core.jwt_ext_custom import (
    jwt_required_with_allnetworks_claim,
    jwt_required_with_management_claim,
)
from core.utils import U

export_management_endpoint = Blueprint("export_management", __name__)


@export_management_endpoint.route("/api/exports/authorities", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "authorities")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "authorities.csv")


@export_management_endpoint.route("/api/exports/zones", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_zones():
    with CursorFromPool() as cursor:
        m = Management(cursor, "zones")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "zones.csv")


@export_management_endpoint.route("/api/exports/networks", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "networks.csv")


@export_management_endpoint.route("/api/exports/stations", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "stations.csv")


@export_management_endpoint.route("/api/exports/sampling_points", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "sampling_points.csv")


@export_management_endpoint.route("/api/exports/processes", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "processes.csv")


@export_management_endpoint.route("/api/exports/documents", methods=["GET"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_documents():
    with CursorFromPool() as cursor:
        m = Management(cursor, "documents")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "documents.csv")