from datetime import datetime

from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from core.database import CursorFromPool
from core.query import Q
from endpoints.qualitycontrol.verify.models import DatasetModel, FlagModel
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim
from core.log_context import set_log_context

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
                    COALESCE (min(aa.c) FILTER (WHERE observationverification_id = 1),0) AS verified, 
                    COALESCE (min(aa.c) FILTER (WHERE observationverification_id = 2),0) AS pre_verified, 
                    COALESCE (min(aa.c) FILTER (WHERE observationverification_id = 3),0) AS not_verified								
                from 
                (
                  select s.name, p.id, EXTRACT(year FROM o.from_time) as year,EXTRACT(month FROM o.from_time) as month, COALESCE(NULLIF(po.notation, ''), po.label) pollutant, COALESCE(NULLIF(t.notation, ''), t.label) as timestep, o.observationverification_id, count(*) as c
                  from stations s
                  join network_access n on n.id = s.network_id
                  join sampling_points p on s.id = p.station_id
                  join observations o on p.id = o.sampling_point_id
                  -- LEFT: pollutant_id / time_resolution_id are nullable since migration
                  -- 012. As inner joins these hid whole months of a local-pollutant series
                  -- from Verify, even though the observations were there to approve.
                  left join eea_pollutants po on p.pollutant_id = po.id
                  left join eea_times t on p.time_resolution_id = t.id
                  where EXTRACT(year FROM o.from_time) = %(year)s
                  and s.id = %(station_id)s
                  group by s.name, EXTRACT(year FROM o.from_time), EXTRACT(month FROM o.from_time), o.observationverification_id, COALESCE(NULLIF(po.notation, ''), po.label), p.id, t.notation, t.label
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
            select 
                st.id, 
                st.name, 
                min(extract(year from sp.from_time))::int as from_year, 
                max(extract(year from sp.to_time))::int as to_year
            from stations st, sampling_points sp, network_access n
            where sp.station_id = st.id
            and n.id = st.network_id
            and from_time is not null
            and to_time is not null
            group by st.id, st.name
            order by LOWER(st.name)
        """, n_param)
        stations = cursor.fetchall()
        return jsonify(stations)


@verify_endpoint.route('/api/qualitycontrol/verify/flag', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def flag():
    m = FlagModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    # Half-open month window rather than EXTRACT(year/month FROM from_time): only a
    # range predicate can use idx_observations_spid_ft (sampling_point_id, from_time).
    month_start = datetime(m.year, m.month, 1)
    next_month = datetime(m.year + 1, 1, 1) if m.month == 12 else datetime(m.year, m.month + 1, 1)

    with CursorFromPool() as cursor:
        set_log_context(cursor, 'qc_verify')
        cursor.execute("""
            update observations
            set observationverification_id = %(level)s
            where sampling_point_id = %(sampling_point_id)s
            and from_time >= %(month_start)s
            and from_time < %(next_month)s
        """, {
            "level": m.level,
            "sampling_point_id": m.sampling_point_id,
            "month_start": month_start,
            "next_month": next_month,
        })
        if cursor.rowcount == 0:
            raise BadRequest("Could set verification flag")
        return jsonify({"success": True})
