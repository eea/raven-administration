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
          SELECT st.id,
                st.name,
                st.begin_position,
                st.end_position,
                st.network_id,
                st.city,
                st.national_station_code,
                st.media_monitored,
                st.mobile,
                st.measurement_regime,
                st.area_classification,
                st.distance_junction,
                st.traffic_volume,
                st.heavy_duty_fraction::DOUBLE PRECISION,
                st.height_facades,
                st.municipality,
                st.street_width,
                st.eoi_code,
                ST_X(st.geom)    longitude,
                ST_Y(st.geom)    latitude,
                ST_Z(st.geom)    altitude,
                ST_SRID(st.geom) epsg,
                n.name   as      network,
                mv.label as      media_monitored_name,
                mr.label as      measurement_regime_name,
                ac.label as      area_classification_name
          FROM stations st
                  LEFT OUTER JOIN eea_mediavalues mv ON lower(st.media_monitored) = lower(mv.id)
                  LEFT OUTER JOIN eea_measurementregimevalues mr ON lower(st.measurement_regime) = lower(mr.id)
                  LEFT OUTER JOIN eea_areaclassifications ac ON lower(st.area_classification) = lower(ac.id),
              networks n
          WHERE st.network_id = n.id
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
