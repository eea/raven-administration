from flask import jsonify, Blueprint, request, Response
from api.core.database import CursorFromPool
from api.core.data.management import Management
from api.core.jwt_ext_custom import jwt_required_with_allnetworks_claim, jwt_required_with_management_claim
import csv

export_management_endpoint = Blueprint('export_management', __name__)


@export_management_endpoint.route('/api/exports/authorities', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "responsible_authorities")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=authorities.csv"})


@export_management_endpoint.route('/api/exports/zones', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_zones():
    with CursorFromPool() as cursor:
        m = Management(cursor, "zones")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=zones.csv"})


@export_management_endpoint.route('/api/exports/networks', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=networks.csv"})


@export_management_endpoint.route('/api/exports/stations', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=stations.csv"})


@export_management_endpoint.route('/api/exports/sampling_points', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=sampling_points.csv"})


@export_management_endpoint.route('/api/exports/observing_capabilities', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_observing_capabilities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "observing_capabilities")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=observing_capabilities.csv"})


@export_management_endpoint.route('/api/exports/samples', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_samples():
    with CursorFromPool() as cursor:
        m = Management(cursor, "samples")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=samples.csv"})


@export_management_endpoint.route('/api/exports/processes', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.generic_select()
        return Response(
            m.df.to_csv(index=False, quoting=csv.QUOTE_ALL),
            mimetype="text/csv",
            headers={"Content-disposition":
                     "attachment; filename=processes.csv"})
