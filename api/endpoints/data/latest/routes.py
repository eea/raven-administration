from flask import jsonify, Blueprint
from api.core.database import CursorFromPool
from api.core.jwt_ext_custom import jwt_required_with_observations_claim

latest_endpoint = Blueprint('latest', __name__)


@latest_endpoint.route('/api/data/latest', methods=['GET'])
@jwt_required_with_observations_claim()
def latest():
    with CursorFromPool() as cursor:
        sql = """
			      select sp.id as id, to_char(sp.from_time,'yyyy-mm-dd HH24:mi') as from_time, to_char(sp.to_time,'yyyy-mm-dd HH24:mi') as to_time, o.value::double PRECISION, o.validation_flag, o.verification_flag, p.notation as pollutant, t.label as timestep, s.name as station, n.name as network, u.notation as unit
            from observations o, sampling_points sp, eea_pollutants p, eea_times t, stations s, networks n, eea_concentrations u
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
        cursor.execute(sql)
        values = cursor.fetchall()
        return jsonify(values)
