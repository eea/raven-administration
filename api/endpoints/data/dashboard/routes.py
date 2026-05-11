from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.data.mean import Mean, MeanType
from core.query import Q
from endpoints.data.historical.models import HistoricalModel

dashboard_endpoint = Blueprint('dashboard', __name__)


@dashboard_endpoint.route('/api/data/dashboard/sampling_points', methods=['GET'])
@jwt_required_with_data_claim()
def sampling_points():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            SELECT
                s.name AS station,
                COALESCE(NULLIF(po.notation, ''), po.label) AS pollutant,
                t.notation AS timestep,
                u.notation AS unit,
                lp.equipment,
                lp.equipment_identifier,
                sp.id AS sampling_point_id,
                to_char(sp.from_time, 'YYYY-MM-DD HH24:MI') AS fromtime,
                to_char(sp.to_time,   'YYYY-MM-DD HH24:MI') AS totime
            FROM network_access n
            JOIN stations s ON n.id = s.network_id
            JOIN sampling_points sp ON s.id = sp.station_id
            JOIN eea_pollutants po ON sp.pollutant_id = po.id
            JOIN eea_times t ON sp.time_resolution_id = t.id
            JOIN eea_concentrations u ON sp.unit_id = u.id
            LEFT JOIN (
                SELECT DISTINCT ON (pr.sampling_point_id)
                    pr.sampling_point_id,
                    COALESCE(NULLIF(me.notation, ''), me.label) AS equipment,
                    pr.equipment_identifier
                FROM processes pr
                LEFT JOIN eea_measurementequipments me ON pr.equipment_id = me.id
                ORDER BY pr.sampling_point_id, pr.activity_begin DESC
            ) lp ON lp.sampling_point_id = sp.id
            ORDER BY LOWER(s.name), LOWER(COALESCE(NULLIF(po.notation, ''), po.label)), LOWER(t.notation)
        """, n_param)
        return jsonify(cursor.fetchall())


@dashboard_endpoint.route('/api/data/dashboard', methods=['POST'])
@jwt_required_with_data_claim()
def dashboard():
    with CursorFromPool() as cursor:
        m = HistoricalModel(**request.json)
        sampling_point_ids = Q.sampling_point_ids_by_networks_access(m.sampling_point_ids)
        if not sampling_point_ids:
            return jsonify([])
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True)
        return jsonify(meanvalues)
