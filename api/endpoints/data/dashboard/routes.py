from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.data.mean import Mean, MeanType
from core.query import Q
from core import series_metadata as smeta
from endpoints.data.historical.models import HistoricalModel

dashboard_endpoint = Blueprint('dashboard', __name__)


@dashboard_endpoint.route('/api/data/dashboard/sampling_points', methods=['GET'])
@jwt_required_with_data_claim()
def sampling_points():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        # Local component / unit / timestep for series that have no EEA vocabulary term.
        # Plugin-supplied, and identical to the bare EEA column when no plugin provides
        # them; the EEA term always wins. See core/series_metadata.py.
        # Bound to names because ORDER BY needs the same expressions: PostgreSQL only
        # accepts a bare output name there, not one inside LOWER(...).
        pollutant = smeta.expr('pollutant', "NULLIF(po.notation, '')", 'po.label')
        timestep = smeta.expr('timestep', 't.notation')
        unit = smeta.expr('unit', 'u.notation')
        cursor.execute(f"""
            {with_network_sql}
            SELECT
                s.name AS station,
                {pollutant} AS pollutant,
                {timestep} AS timestep,
                {smeta.expr('timestep_seconds', 't.timestep')} AS timestep_seconds,
                {unit} AS unit,
                lp.equipment,
                lp.equipment_identifier,
                sp.id AS sampling_point_id,
                to_char(sp.from_time, 'YYYY-MM-DD HH24:MI') AS fromtime,
                to_char(sp.to_time,   'YYYY-MM-DD HH24:MI') AS totime,
                EXISTS (SELECT 1 FROM calculated_series cs WHERE cs.result = sp.id) AS is_calculated,
                sp.daily_check AS is_daily_check
            FROM network_access n
            JOIN stations s ON n.id = s.network_id
            JOIN sampling_points sp ON s.id = sp.station_id
            -- LEFT: nullable measurement config since migration 012. Access is enforced
            -- by network_access above, not by the vocabulary joins.
            LEFT JOIN eea_pollutants po ON sp.pollutant_id = po.id
            LEFT JOIN eea_times t ON sp.time_resolution_id = t.id
            LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
            LEFT JOIN (
                SELECT DISTINCT ON (pr.sampling_point_id)
                    pr.sampling_point_id,
                    COALESCE(NULLIF(me.notation, ''), me.label) AS equipment,
                    pr.equipment_identifier
                FROM processes pr
                LEFT JOIN eea_measurementequipments me ON pr.equipment_id = me.id
                ORDER BY pr.sampling_point_id, pr.process_activity_begin DESC
            ) lp ON lp.sampling_point_id = sp.id
            {smeta.joins('sp')}
            -- Ordered by the composed expressions, so a local series sorts among the
            -- others instead of trailing as a NULL pollutant.
            ORDER BY LOWER(s.name), LOWER({pollutant}), LOWER({timestep})
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
        # pluginMetadata: the plot builds its legend label from `component`/`unit` and
        # groups its y axes by `unit`, so a series with no EEA term needs the local one
        # or it lands unlabelled on a shared NULL axis. Opt-in per call site -- see
        # Mean.GetTimeseries for why the exports and attainment paths must not have it.
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True, pluginMetadata=True)
        return jsonify(meanvalues)
