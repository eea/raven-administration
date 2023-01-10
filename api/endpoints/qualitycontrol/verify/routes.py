from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from core.database import CursorFromPool
from core.query import Q
from endpoints.qualitycontrol.verify.models import DatasetModel, FlagModel
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim

verify_endpoint = Blueprint('verify', __name__)


@verify_endpoint.route('/api/qualitycontrol/verify/datasets', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def datasets():
    m = DatasetModel(**request.json)
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        params = {
            "station_id": m.station_id,
            "year": m.year,
            "networkids": n_param["networkids"]
        }
        cursor.execute(f"""
            {with_network_sql}
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
                  from stations s, sampling_points p, observations o,  eea_pollutants po, eea_times t, network_access n
                  where EXTRACT(year FROM o.from_time) = %(year)s
                  and n.id = s.network_id
                  and s.id = %(station_id)s
                  and s.id = p.station_id
                  and p.id = o.sampling_point_id
                  and p.pollutant = po.uri
                  and p.timestep = t.id
                  group by s.name, EXTRACT(year FROM o.from_time), EXTRACT(month FROM o.from_time), o.verification_flag, po.notation, p.id, t.label
                ) aa
                group by aa.name,aa.id, aa.year, aa.month, aa.pollutant, aa.timestep
            """, params)
        datasets = cursor.fetchall()
        return jsonify(datasets)


@verify_endpoint.route('/api/qualitycontrol/verify/stations', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def stations():
    with_network_sql, n_param = Q.with_networks_by_access_as_sql()
    with CursorFromPool() as cursor:
        cursor.execute(f"""
            {with_network_sql}
            select st.id, st.name, min(extract(year from sp.from_time)) from_year, max(extract(year from sp.to_time)) to_year
            from stations st, sampling_points sp, network_access n
            where sp.station_id = st.id
            and n.id = st.network_id
            and from_time is not null
            and to_time is not null
            group by st.id, st.name
            order by st.name
        """, n_param)
        stations = cursor.fetchall()
        return jsonify(stations)


@verify_endpoint.route('/api/qualitycontrol/verify/flag', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def flag():
    m = FlagModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

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
