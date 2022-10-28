from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from api.core.database import CursorFromPool
from api.endpoints.qualitycontrol.validate.models import TimevalueModel, FlagModel
from api.core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim

validate_endpoint = Blueprint('validate', __name__)


@validate_endpoint.route('/api/qualitycontrol/validate/timevalues', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def timevalues():
    m = TimevalueModel(**request.json)
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
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
              aa.value,
              CONCAT(aa.name,', ', aa.pollutant,', ', aa.timestep, ', ', aa.unit ) as label,
                  to_char(aa.fromtime, 'YYYY-MM-DD"T"HH24:MI:SS') as fromtime,
                  to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime
              FROM
            (
              SELECT sp.id as sp, sp.id as value, s.name, po.notation pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.label as timestep, u.notation as unit
                FROM
                    stations s,
                    sampling_points sp,
                    eea_pollutants po,
                    eea_times t,
                    eea_concentrations u
                WHERE 1=1
                    and s.id = sp.station_id
                    and sp.pollutant = po.uri
                    and sp.timestep = t.id
                    and sp.concentration = u.id
                    and sp.from_time is not null
                    and sp.to_time is not null
                GROUP by s.name, sp.id, sp.pollutant,sp.id, po.notation, sp.from_time,  sp.to_time, t.label, u.notation
            ) aa
            order by label
        """)
        timeseries = cursor.fetchall()
        return jsonify(timeseries)
