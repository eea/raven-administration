from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from api.core.database import CursorFromPool
from api.endpoints.processing.scale.models import ScalingpointModel


scale_endpoint = Blueprint('scale', __name__)


@scale_endpoint.route("/api/processing/scale/scaling_points", methods=['POST'])
@jwt_required()
def scaling_points():
    with CursorFromPool() as cursor:
        model = ScalingpointModel(**request.json)
        cursor.execute("""
            select 
              id, 
              zero_point::DOUBLE PRECISION, 
              span_value::DOUBLE PRECISION, 
              gas_concentration::DOUBLE PRECISION, 
              to_char(timestamp, 'YYYY-MM-DD HH24') as timestamp, 
              to_char(timestamp, 'YYYY-MM-DD HH24:MI:SS') as datetime, 
              createdby, 
              sampling_point_id
            from scaling_points
            where sampling_point_id = %(sampling_point_id)s
            order by timestamp
        """, model)
        convertions = cursor.fetchall()
        return jsonify(convertions)

## LOOKUPS ##


@scale_endpoint.route('/api/processing/scale/timeseries', methods=['GET'])
@jwt_required()
def timeseries():
    with CursorFromPool() as cursor:
        cursor.execute("""
            with
            timeseries as (
                select CONCAT(s.name,', ', p.notation,', ', t.label, ', ', u.notation )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t, eea_concentrations u
                where sp.station_id = s.id
                and sp.pollutant = p.uri
                and sp.timestep = t.id
                and sp.concentration = u.id
                order by s.name, p.notation, t.label
            ),
            scaling_points_with_timeseries as (
                select distinct sampling_point_id as id from scaling_points
            )
            select t.*, case when sp.id is NULL then false else true end as hasScalingPoint
            from timeseries t
            LEFT JOIN scaling_points_with_timeseries sp
            ON t.value=sp.id
            order by hasScalingPoint desc, t.label
        """)
        timeseries = cursor.fetchall()
        return jsonify(timeseries)
