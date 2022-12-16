from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.stations.models import StationModel, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query_access import Access
from core.query import Q

stations_endpoint = Blueprint('stations', __name__)


@stations_endpoint.route('/api/management/stations', methods=['GET'])
@jwt_required_with_management_claim()
def stations():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
          {with_network_sql} 
          SELECT st.id,
                st.name,
                st.begin_position,
                st.end_position,
                st.network_id,
                st.city,
                st.national_station_code,
                st.media_monitored as media_id,
                st.mobile,
                st.measurement_regime  as measurement_regime_id,
                st.area_classification  as area_classification_id,
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
                mv.label as      media,
                mr.label as      measurement_regime,
                ac.label as      area_classification 
          FROM stations st, eea_mediavalues mv, eea_areaclassifications ac, eea_measurementregimevalues mr, networks n, network_access na
          WHERE st.network_id = n.id
          AND st.area_classification = ac.id
          AND st.media_monitored = mv.id
          AND st.measurement_regime = mr.id 
          AND n.id = na.id
          ORDER BY st.name, st.id
        """, n_param)
        stations = cursor.fetchall()
        return jsonify(stations)


@stations_endpoint.route('/api/management/stations/update', methods=['POST'])
@jwt_required_with_management_claim()
def stations_update():
    with CursorFromPool() as cursor:
        model = StationModel(**request.json)

        if not Access.to_station(model.id):
            raise BadRequest("Access denied for station")

        sql = """ 
            UPDATE stations
            SET 
              name=%(name)s, 
              begin_position=%(begin_position)s, 
              end_position=%(end_position)s, 
              network_id=%(network_id)s, 
              city=%(city)s, 
              national_station_code=%(national_station_code)s, 
              media_monitored=%(media_id)s, 
              mobile=%(mobile)s, 
              measurement_regime=%(measurement_regime_id)s, 
              area_classification=%(area_classification_id)s, 
              distance_junction=%(distance_junction)s, 
              traffic_volume=%(traffic_volume)s, 
              heavy_duty_fraction=%(heavy_duty_fraction)s, 
              street_width=%(street_width)s, 
              height_facades=%(height_facades)s, 
              geom = ST_SetSRID(ST_MakePoint(%(longitude)s,%(latitude)s,%(altitude)s),%(epsg)s),
              municipality=%(municipality)s, 
              eoi_code=%(eoi_code)s
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@stations_endpoint.route('/api/management/stations/insert', methods=['POST'])
@jwt_required_with_management_claim()
def stations_insert():
    with CursorFromPool() as cursor:
        model = StationModel(**request.json)

        if not Access.to_network(model.network_id):
            raise BadRequest("Access denied for network")

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
              %(media_id)s, 
              %(mobile)s, 
              %(measurement_regime_id)s, 
              %(area_classification_id)s, 
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
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@stations_endpoint.route("/api/management/stations/delete", methods=['POST'])
@jwt_required_with_management_claim()
def stations_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if not Access.to_station(model.id):
            raise BadRequest("Access denied for station")

        sql = "delete from stations where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})
