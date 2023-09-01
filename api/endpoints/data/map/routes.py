from flask import jsonify, Blueprint
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.query import Q
map_endpoint = Blueprint('map', __name__)


@map_endpoint.route('/api/data/map', methods=['GET'])
@jwt_required_with_data_claim()
def map():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        sql = f"""
            {with_network_sql}
            select
              n.name as network, s.name as station,st_x(geom) x, st_y(geom) y,
              json_agg(json_build_object(
                      'from_time', to_char(sp.from_time,'yyyy-mm-dd HH24:mi'),
                      'to_time', to_char(sp.to_time,'yyyy-mm-dd HH24:mi'),
                      'value',  o.value::double PRECISION,
                      'validation_flag',  o.validation_flag,
                      'verification_flag',  o.verification_flag,
                      'pollutant',  p.notation,
                      'timestep',  t.label,
                      'unit',  u.notation
              )) as timeseries
          from observations o, sampling_points sp, eea_pollutants p, eea_times t, stations s, network_access n, eea_concentrations u
          where 1=1
          and n.id = s.network_id
          and s.id = sp.station_id
          and o.sampling_point_id = sp.id
          and sp.pollutant = p.uri
          and sp.timestep = t.id
          and o.to_time = sp.to_time
          and sp.concentration = u.id
          group by network, station, x,y
        """
        cursor.execute(sql, n_param)
        values = cursor.fetchall()
        return jsonify(values)
