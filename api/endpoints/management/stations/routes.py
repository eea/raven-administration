from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool

from api.endpoints.management.stations.models import StationModel


stations_endpoint = Blueprint('stations', __name__)


@stations_endpoint.route('/api/management/stations', methods=['GET'])
@jwt_required()
def stations():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select 
                s.id, s.name, 
                s.eoi_code, n.name as network, 
                n.id as network_id , 
                ac.label as area_classification, 
                ac.id as area_classification_id, 
                st_x(geom) as lng, 
                st_y(geom) as lat,
                st_z(geom) as alt,
                st_srid(geom) as epsg
            from stations s, networks n, eea_areaclassifications ac
            where s.network_id = n.id
            and s.area_classification = ac.id
            order by s.name
        """)
        stations = cursor.fetchall()
        return jsonify(stations)


@stations_endpoint.route('/api/management/stations/update', methods=['POST'])
@jwt_required()
def stations_update():
    with CursorFromPool() as cursor:
        model = StationModel(**request.json)
        sql = """ 
            UPDATE stations
            SET name = %(name)s,
            eoi_code = %(eoi_code)s,
            network_id = %(network_id)s,
            area_classification = %(area_classification_id)s,
            geom = ST_Transform(ST_SetSRID(ST_MakePoint(%(lng)s,%(lat)s,%(alt)s),%(epsg)s),4326)
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##


@stations_endpoint.route('/api/management/stations/networks', methods=['GET'])
@jwt_required()
def networks():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from networks r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@stations_endpoint.route('/api/management/stations/classifications', methods=['GET'])
@jwt_required()
def classifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_areaclassifications r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)
