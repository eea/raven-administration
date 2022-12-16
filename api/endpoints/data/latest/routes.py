from flask import jsonify, Blueprint
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.query import Q
latest_endpoint = Blueprint('latest', __name__)


@latest_endpoint.route('/api/data/latest', methods=['GET'])
@jwt_required_with_data_claim()
def latest():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        sql = f"""
            {with_network_sql}
			      select sp.id as id, to_char(sp.from_time,'yyyy-mm-dd HH24:mi') as from_time, to_char(sp.to_time,'yyyy-mm-dd HH24:mi') as to_time, o.value::double PRECISION, o.validation_flag, o.verification_flag, p.notation as pollutant, t.label as timestep, s.name as station, n.name as network, u.notation as unit,
            case
                when sp.to_time > NOW() - INTERVAL '3 hours' then 0
                when sp.to_time > NOW() - INTERVAL '6 months' then 1
                else 2
            end status
            from observations o, sampling_points sp, eea_pollutants p, eea_times t, stations s, network_access n, eea_concentrations u
            where 1=1
            and n.id = s.network_id
            and s.id = sp.station_id
            and o.sampling_point_id = sp.id
            and sp.pollutant = p.uri
            and sp.timestep = t.id
            and o.to_time = sp.to_time
            and sp.concentration = u.id
            order by to_time desc, network, station, pollutant, timestep
        """
        cursor.execute(sql, n_param)
        values = cursor.fetchall()
        return jsonify(values)
