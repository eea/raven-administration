from flask import jsonify, Blueprint, request
from core.data.statistics import Statistics
from endpoints.data.statistics.models import StatisticsModel
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim, get_networks, can_see_all_networks
from core.query import Q

statistics_endpoint = Blueprint('statistics', __name__)


@statistics_endpoint.route('/api/data/statistics/years', methods=['GET'])
@jwt_required_with_data_claim()
def statistics_years():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
        {with_network_sql}
        SELECT 
            EXTRACT(YEAR FROM MIN(sp.from_time))::integer as min_year,
            EXTRACT(YEAR FROM MAX(sp.to_time))::integer as max_year
        FROM sampling_points sp
        JOIN stations s ON sp.station_id = s.id
        JOIN network_access n ON s.network_id = n.id
        WHERE sp.from_time IS NOT NULL 
        AND sp.to_time IS NOT NULL
        """, n_param)
        result = cursor.fetchone()

    if not result:
        return jsonify([])

    min_year = result['min_year']
    max_year = result['max_year']

    if min_year is None or max_year is None:
        return jsonify([])

    # Generate list of all years between min and max (inclusive) in reverse order
    years = list(range(max_year, min_year - 1, -1))

    return jsonify(years)


@statistics_endpoint.route('/api/data/statistics/pollutants_and_aggregationprocess', methods=['GET'])
@jwt_required_with_data_claim()
def statistics_pollutants_and_aggregation_process():
    with CursorFromPool() as cursor:
        cursor.execute(f""" 
        SELECT
          pol.notation AS pollutant,
          array_agg(ARRAY[
            ap.notation,
            s.directive_2008_50::text,
            s.directive_2024_2881::text
          ] ORDER BY ap.notation) AS ap_with_directives
        FROM statistics s
        JOIN eea_pollutants pol
          ON s.pollutant_uri = pol.uri
        JOIN eea_aggregationprocess ap
          ON s.aggregation_process_id = ap.id
        GROUP BY pol.notation
        ORDER BY pollutant;
        """)
        result = cursor.fetchall()

    return jsonify(result)


@statistics_endpoint.route('/api/data/statistics/values', methods=['POST'])
@jwt_required_with_data_claim()
def statistics_values():
    with CursorFromPool() as cursor:
        m = StatisticsModel(**request.json)
        statistics = Statistics(cursor)
        
        # Generate statistics for all requested years
        all_statistics_data = []
        for year in m.year_list:
            year_data = statistics.generate(m.aggregation_process, m.pollutant, year)
            all_statistics_data.extend(year_data)

        # Apply network filtering
        if not can_see_all_networks():
            user_networks = get_networks()
            all_statistics_data = [row for row in all_statistics_data if row['network'] in user_networks]

        return jsonify(all_statistics_data)
