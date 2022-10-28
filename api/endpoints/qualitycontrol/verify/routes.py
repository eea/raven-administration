from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from api.core.database import CursorFromPool
from api.endpoints.qualitycontrol.verify.models import DatasetModel, FlagModel
from api.core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim

verify_endpoint = Blueprint('verify', __name__)


@verify_endpoint.route('/api/qualitycontrol/verify/datasets', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def datasets():
    m = DatasetModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            select 
                    aa.name as station,
                    aa.id, 
                    aa.year, 
                    aa.month,
                    aa.pollutant,
                    aa.timestep,
                    COALESCE (min(aa.c) FILTER (WHERE verification_flag = 1),0) AS verified, 
                    COALESCE (min(aa.c) FILTER (WHERE verification_flag = 2),0) AS pre_verified, 
                    COALESCE (min(aa.c) FILTER (WHERE verification_flag = 3),0) AS not_verified								
                from 
                (
                  select s.name, p.id, EXTRACT(year FROM o.from_time) as year,EXTRACT(month FROM o.from_time) as month, po.notation pollutant, t.label as timestep, o.verification_flag, count(*) as c
                  from stations s, sampling_points p, observations o,  eea_pollutants po, eea_times t
                  where EXTRACT(year FROM o.from_time) = %(year)s
                  and s.id = %(station_id)s
                  and s.id = p.station_id
                  and p.id = o.sampling_point_id
                  and p.pollutant = po.uri
                  and p.timestep = t.id
                  group by s.name, EXTRACT(year FROM o.from_time), EXTRACT(month FROM o.from_time), o.verification_flag, po.notation, p.id, t.label
                ) aa
                group by aa.name,aa.id, aa.year, aa.month, aa.pollutant, aa.timestep
            """, m)
        datasets = cursor.fetchall()
        return jsonify(datasets)


@verify_endpoint.route('/api/qualitycontrol/verify/stations', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def stations():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select st.id, st.name, min(extract(year from sp.from_time)) from_year, max(extract(year from sp.from_time)) to_year
            from stations st, sampling_points sp
            where sp.station_id = st.id
            and from_time is not null
            and to_time is not null
            group by st.id, st.name
            order by st.name
        """)
        stations = cursor.fetchall()
        return jsonify(stations)


@verify_endpoint.route('/api/qualitycontrol/verify/flag', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def flag():
    m = FlagModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            update observations
            set verification_flag = %(level)s
            where EXTRACT(year FROM from_time) = %(year)s
            and EXTRACT(month FROM from_time) = %(month)s            
            and sampling_point_id = %(sampling_point_id)s
        """, m)
        if cursor.rowcount == 0:
            raise BadRequest("Could set verification flag")
        return jsonify({"success": True})


## LOOKUPS ##

# @verify_endpoint.route('/api/qualitycontrol/verify/timeseries', methods=['GET'])
# @jwt_required()
# def timeseries():
#     with CursorFromPool() as cursor:
#         cursor.execute("""
#             SELECT
#               aa.value,
#               CONCAT(aa.name,', ', aa.pollutant,', ', aa.timestep, ', ', aa.unit ) as label,
#                   to_char(aa.fromtime, 'YYYY-MM-DD"T"HH24:MI:SS') as fromtime,
#                   to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime
#               FROM
#             (
#               SELECT sp.id as sp, sp.id as value, s.name, po.notation pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.label as timestep, u.notation as unit
#                 FROM
#                     stations s,
#                     sampling_points sp,
#                     eea_pollutants po,
#                     eea_times t,
#                     eea_concentrations u
#                 WHERE 1=1
#                     and s.id = sp.station_id
#                     and sp.pollutant = po.uri
#                     and sp.timestep = t.id
#                     and sp.concentration = u.id
#                     and sp.from_time is not null
#                     and sp.to_time is not null
#                 GROUP by s.name, sp.id, sp.pollutant,sp.id, po.notation, sp.from_time,  sp.to_time, t.label, u.notation
#             ) aa
#             order by label
#         """)
#         timeseries = cursor.fetchall()
#         return jsonify(timeseries)
