import math
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
            SELECT
                sp.id AS id,
                to_char(sp.from_time, 'yyyy-mm-dd HH24:mi') AS from_time,
                to_char(sp.to_time,   'yyyy-mm-dd HH24:mi') AS to_time,
                o.observationvalidity_id,
                o.observationverification_id,
                COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant,
                t.notation           AS timestep,
                s.name               AS station,
                n.name               AS network,
                u.notation           AS unit,
                COALESCE(NULLIF(me.notation, ''), me.label) AS equipment,
                pr.equipment_identifier,
                CASE
                    WHEN sp.to_time > NOW() - INTERVAL '3 hours'  THEN 0
                    WHEN sp.to_time > NOW() - INTERVAL '6 months' THEN 1
                    ELSE 2
                END                   AS status,
                NULLIF(o.value, 'NaN')::double precision AS value,
                
                a_local.level        AS local_aqi_level,
                a_local.description  AS local_aqi_desc,
                a_local.color        AS local_aqi_color,
                
                a_eea.level          AS eea_aqi_level,
                a_eea.description    AS eea_aqi_desc,
                a_eea.color          AS eea_aqi_color
            FROM
                observations             o
                JOIN sampling_points     sp ON o.sampling_point_id = sp.id
                JOIN eea_pollutants      p  ON sp.pollutant_id    = p.id
                JOIN eea_times           t  ON sp.time_resolution_id = t.id
                JOIN stations            s  ON sp.station_id       = s.id
                JOIN network_access      n  ON s.network_id        = n.id
                JOIN eea_concentrations  u  ON sp.unit_id          = u.id
                LEFT JOIN (
                    SELECT DISTINCT ON (pr.sampling_point_id)
                        pr.sampling_point_id,
                        pr.equipment_identifier,
                        pr.equipment_id
                    FROM processes pr
                    ORDER BY pr.sampling_point_id, pr.activity_begin DESC
                ) pr ON pr.sampling_point_id = sp.id
                LEFT JOIN eea_measurementequipments me ON me.id = pr.equipment_id
                
                LEFT JOIN public.aqi AS a_local
                    ON a_local.pollutant_id    = sp.pollutant_id
                  AND a_local.timestep         = sp.time_resolution_id
                  AND a_local.calculation_type = 'LOCAL'
                  AND a_local.range @> ROUND(NULLIF(o.value, 'NaN')::numeric)
                
                LEFT JOIN public.aqi AS a_eea
                    ON a_eea.pollutant_id      = sp.pollutant_id
                  AND a_eea.timestep           = sp.time_resolution_id
                  AND a_eea.calculation_type   = 'EEA'
                  AND a_eea.range @> ROUND(NULLIF(o.value, 'NaN')::numeric)
            WHERE
                1 = 1
                AND o.to_time = sp.to_time
            ORDER BY
                o.to_time  DESC,
                station,
                pollutant,
                timestep;
        """
        cursor.execute(sql, n_param)
        values = cursor.fetchall()

        return jsonify(values)
