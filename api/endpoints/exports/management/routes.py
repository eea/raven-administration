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
import zipfile

export_management_endpoint = Blueprint("export_management", __name__)


@export_management_endpoint.route("/api/exports/authorities", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "responsible_authorities")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "authorities.csv")


@export_management_endpoint.route("/api/exports/zones", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_zones():
    with CursorFromPool() as cursor:
        m = Management(cursor, "zones")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "zones.csv")


@export_management_endpoint.route("/api/exports/networks", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "networks.csv")


@export_management_endpoint.route("/api/exports/stations", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "stations.csv")


@export_management_endpoint.route("/api/exports/sampling_points", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "sampling_points.csv")


@export_management_endpoint.route(
    "/api/exports/observing_capabilities", methods=["POST"]
)
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_observing_capabilities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "observing_capabilities")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "observing_capabilities.csv")


@export_management_endpoint.route("/api/exports/samples", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_samples():
    with CursorFromPool() as cursor:
        m = Management(cursor, "samples")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "samples.csv")


@export_management_endpoint.route("/api/exports/processes", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "processes.csv")


@export_management_endpoint.route("/api/exports/attainments", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_attainments():
    with CursorFromPool() as cursor:
        m = Management(cursor, "attainments")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "attainments.csv")


@export_management_endpoint.route("/api/exports/assessmentregime", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_assessmentregime():
    with CursorFromPool() as cursor:

        m = Management(cursor, "assessmentregime")
        m.sql_select("select * from assessmentregimes")

        md = Management(cursor, "assessmentdata")
        md.sql_select("select * from assessmentdata")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.writestr("assessmentregimes.csv", m.df.to_csv(index=False, quoting=csv.QUOTE_ALL))
            zip_file.writestr("assessmentdata.csv", md.df.to_csv(index=False, quoting=csv.QUOTE_ALL))

        zip_buffer.seek(0)
        return U.zip_response(zip_buffer, "assessmentregimes.zip")


@export_management_endpoint.route("/api/exports/exceedances", methods=["POST"])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_exceedances():
    with CursorFromPool() as cursor:
      
        m = Management(cursor, "exceedancedescriptions")
        m.sql_select("select * from exceedancedescriptions")

        md = Management(cursor, "exceedingmethods")
        md.sql_select(
          """
            SELECT ass.*
              FROM exceedancedescriptions ed,
                attainments at,
                assessmentregimes ar,
                assessmentdata ass
              WHERE 1=1
                AND ed.attainment_id = at.id
                AND at.assessmentregime_id = ar.id
                AND ass.assessmentregime_id = ar.id
          """
        )
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
              zip_file.writestr("exceedancedescriptions.csv", m.df.to_csv(index=False, quoting=csv.QUOTE_ALL))
              zip_file.writestr("exceedingmethods.csv", md.df.to_csv(index=False, quoting=csv.QUOTE_ALL))

        zip_buffer.seek(0)
        return U.zip_response(zip_buffer, "exceedancedescriptions.zip")
