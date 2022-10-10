from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from api.core.database import CursorFromPool


scale_endpoint = Blueprint('scale', __name__)


## LOOKUPS ##
@scale_endpoint.route('/api/processing/scale/timeseries', methods=['GET'])
@jwt_required()
def timeseries():
    with CursorFromPool() as cursor:
        cursor.execute("""
            with
            timeseries as (
                select CONCAT(s.name,', ', p.notation,', ', t.label )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t
                where sp.station_id = s.id
                and sp.pollutant = p.uri
                and sp.timestep = t.id
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
