from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from core.database import CursorFromPool
from core.query import Q
from endpoints.qualitycontrol.validate.models import TimevalueModel, FlagModel
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim

validate_endpoint = Blueprint('validate', __name__)


@validate_endpoint.route('/api/qualitycontrol/validate/timevalues', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def timevalues():
    m = TimevalueModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
              o.id,
              to_char (o.from_time, 'YYYY-MM-DD HH24:MI:SS') as "fromtime",
              to_char (o.to_time, 'YYYY-MM-DD HH24:MI:SS') as "totime",
              o.sampling_point_id as "sampling_point_id",
              o.validation_flag,
              o.verification_flag,
              o.value::double PRECISION
            FROM observations o
            WHERE 1=1
            AND o.from_time >= %(from_dt)s
            AND o.from_time < %(to_dt)s
            AND  o.sampling_point_id = %(sampling_point_id)s
            order by from_time
        """, m)
        timevalues = cursor.fetchall()
        return jsonify(timevalues)


@validate_endpoint.route('/api/qualitycontrol/validate/flag', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def flag():
    m = FlagModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        cursor.execute("""
            update observations
            set validation_flag = %(flag)s
            where id in %(ids_tuple)s
        """, m)
        if cursor.rowcount == 0:
            raise BadRequest("Could set validation flag")
        return jsonify({"success": True})


## LOOKUPS ##

@validate_endpoint.route('/api/qualitycontrol/validate/timeseries', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def timeseries():
    timeseries = timeseries = Q.timeseries_with_time_by_access()
    return jsonify(timeseries)
