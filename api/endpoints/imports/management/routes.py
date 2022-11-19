from flask import jsonify, Blueprint, request
from api.core.database import CursorFromPool
from api.core.data.management import Management
from api.core.jwt_ext_custom import jwt_required_with_allnetworks_claim

import_management_endpoint = Blueprint('import_management', __name__)


@import_management_endpoint.route('/api/imports/authorities', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "responsible_authorities")
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/networks', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/stations', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.parse_file(request.files["csv"])
        sql = """ 
            INSERT INTO stations (
              id, 
              name, 
              begin_position, 
              end_position, 
              network_id, 
              city, 
              national_station_code, 
              media_monitored, 
              mobile, 
              measurement_regime, 
              area_classification, 
              distance_junction, 
              traffic_volume, 
              heavy_duty_fraction, 
              street_width, 
              height_facades, 
              geom, 
              municipality, 
              eoi_code
            )
            VALUES (
              %(id)s, 
              %(name)s, 
              %(begin_position)s, 
              %(end_position)s, 
              %(network_id)s, 
              %(city)s, 
              %(national_station_code)s, 
              %(media_monitored)s, 
              %(mobile)s, 
              %(measurement_regime)s, 
              %(area_classification)s, 
              %(distance_junction)s, 
              %(traffic_volume)s, 
              %(heavy_duty_fraction)s, 
              %(street_width)s, 
              %(height_facades)s, 
              ST_Transform(ST_SetSRID(ST_MakePoint(%(longitude)s,%(latitude)s,%(altitude)s),%(epsg)s),4326), 
              %(municipality)s, 
              %(eoi_code)s
            )           
        """
        m.sql_insert(sql)
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/sampling_points', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/observing_capabilities', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_observing_capabilities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "observing_capabilities")
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/samples', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_samples():
    with CursorFromPool() as cursor:
        m = Management(cursor, "samples")
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})


@import_management_endpoint.route('/api/imports/processes', methods=['POST'])
@jwt_required_with_allnetworks_claim()
def import_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.parse_file(request.files["csv"])
        m.generic_insert()
        return jsonify({"success": True})
