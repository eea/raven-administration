"""
API routes for air quality exceedances evaluation.

Provides endpoints to:
- List zones and their assessment regimes
- Evaluate exceedances for zones against directive thresholds
- Compare directive requirements
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from .models import ExceedancesZoneModel, ExceedancesRegimeModel
from core.data.exceedances import Exceedances
from core.data.statistics import Statistics


exceedances_endpoint = Blueprint('data_exceedances', __name__)


@exceedances_endpoint.route('/api/data/exceedances/sampling_points', methods=['GET'])
@jwt_required_with_data_claim()
def get_sampling_points():
    """
    Get all sampling points with pollutant information.
    
    Query Parameters:
        pollutant (str): Optional pollutant filter (e.g., 'NO2', 'PM10')
    
    Returns:
        JSON array of sampling points with id, code, pollutant, station info
    
    Example:
        GET /api/data/exceedances/sampling_points?pollutant=NO2
    """
    pollutant = request.args.get('pollutant')
    
    with CursorFromPool() as cursor:
        where_clause = ""
        params = {}
        
        if pollutant:
            where_clause = "WHERE UPPER(p.notation) = UPPER(%(pollutant)s)"
            params['pollutant'] = pollutant
        
        cursor.execute(f"""
            SELECT 
                sp.id,
                sp.code,
                p.notation as pollutant,
                p.label as pollutant_label,
                st.name as station_name,
                st.eoi_code as station_code,
                n.name as network_name
            FROM sampling_points sp
            JOIN eea_pollutants p ON sp.pollutant = p.uri
            JOIN stations st ON sp.station_id = st.id
            JOIN networks n ON st.network_id = n.id
            {where_clause}
            ORDER BY p.notation, st.name, sp.code
        """, params)
        
        sampling_points = cursor.fetchall()
    
    return jsonify(sampling_points), 200


@exceedances_endpoint.route('/api/data/exceedances/regimes', methods=['GET'])
@jwt_required_with_data_claim()
def get_regimes():
    """
    Get assessment regimes for a zone.
    
    Query Parameters:
        zone_id (str): Zone identifier (required)
        pollutant (str): Optional pollutant filter (e.g., 'NO2', 'PM10')
    
    Returns:
        JSON array of assessment regimes
    
    Example:
        GET /api/data/exceedances/regimes?zone_id=NO_ZONE_OSLO_2023&pollutant=NO2
    """
    zone_id = request.args.get('zone_id')
    pollutant = request.args.get('pollutant')
    
    if not zone_id:
        return jsonify({"error": "zone_id parameter is required"}), 400
    
    with CursorFromPool() as cursor:
        exc = Exceedances(cursor)
        regimes = exc.get_assessment_regimes(zone_id, pollutant)
    
    return jsonify(regimes), 200


@exceedances_endpoint.route('/api/data/exceedances/directives', methods=['GET'])
@jwt_required_with_data_claim()
def get_directives():
    """
    Get list of available directives for dropdown selection.
    
    Returns:
        JSON array of directive objects with id and label
    
    Example:
        GET /api/data/exceedances/directives
    """
    directives = [
        {"id": "2008/50", "label": "Directive 2008/50/EC"},
        {"id": "2024/2881", "label": "Directive 2024/2881"},
        {"id": "WHO", "label": "WHO Air Quality Guidelines"}
    ]
    
    return jsonify(directives), 200


@exceedances_endpoint.route('/api/data/exceedances/pollutants', methods=['GET'])
@jwt_required_with_data_claim()
def get_pollutants():
    """
    Get list of pollutants with available thresholds.
    
    Query Parameters:
        directive (str): Optional directive filter
    
    Returns:
        JSON array of pollutant objects
    
    Example:
        GET /api/data/exceedances/pollutants?directive=2024/2881
    """
    from core.data.exceedances import DIRECTIVE_THRESHOLDS, POLLUTANT_URIS
    
    directive = request.args.get('directive')
    
    pollutants = []
    for notation, uri in POLLUTANT_URIS.items():
        if notation in DIRECTIVE_THRESHOLDS:
            # Check if pollutant has thresholds for the specified directive
            if directive:
                has_threshold = False
                for objecttype, objectives in DIRECTIVE_THRESHOLDS[notation].items():
                    for obj_name, obj_data in objectives.items():
                        if directive in obj_data:
                            has_threshold = True
                            break
                    if has_threshold:
                        break
                
                if not has_threshold:
                    continue
            
            pollutants.append({
                "notation": notation,
                "uri": uri,
                "label": notation  # Could be enhanced with full names
            })
    
    return jsonify(sorted(pollutants, key=lambda x: x['notation'])), 200


@exceedances_endpoint.route('/api/data/exceedances/evaluate', methods=['POST'])
@jwt_required_with_data_claim()
def evaluate_exceedances():
    """
    Evaluate exceedances for sampling points.
    
    Request Body:
        {
            "year": 2023,
            "pollutant": "NO2",
            "directive": "2024/2881",
            "aggregation_process": "P1Y"  // optional - evaluates specific statistic
        }
    
    Returns:
        JSON array of exceedance evaluation results per sampling point
    
    Example:
        POST /api/data/exceedances/evaluate
        {
            "year": 2023,
            "pollutant": "NO2",
            "directive": "2024/2881"
        }
    """
    data = request.json
    year = data.get('year')
    pollutant = data.get('pollutant')
    directive = data.get('directive')
    aggregation_process = data.get('aggregation_process')
    
    if not year or not pollutant or not directive:
        return jsonify({"error": "year, pollutant, and directive are required"}), 400
    
    with CursorFromPool() as cursor:
        from core.data.exceedances import DIRECTIVE_THRESHOLDS
        
        # Get statistics for this pollutant and year
        statistics = Statistics(cursor)
        
        # Get all aggregation processes for this pollutant from thresholds
        results = []
        
        if pollutant in DIRECTIVE_THRESHOLDS:
            for objecttype, objectives in DIRECTIVE_THRESHOLDS[pollutant].items():
                for obj_name, obj_data in objectives.items():
                    if directive in obj_data:
                        stat = obj_data['statistic']
                        
                        # Skip if filtering by specific aggregation process
                        if aggregation_process and stat != aggregation_process:
                            continue
                        
                        try:
                            # Generate statistics
                            stats_data = statistics.generate(stat, pollutant, year)
                            
                            threshold = obj_data[directive]
                            
                            # Evaluate each sampling point
                            for row in stats_data:
                                exceeded = False
                                if threshold['operator'] == '>':
                                    exceeded = row['value'] > threshold['value']
                                elif threshold['operator'] == '>=':
                                    exceeded = row['value'] >= threshold['value']
                                elif threshold['operator'] == '<':
                                    exceeded = row['value'] < threshold['value']
                                elif threshold['operator'] == '<=':
                                    exceeded = row['value'] <= threshold['value']
                                
                                results.append({
                                    'sampling_point_id': row['spo'],
                                    'sampling_point_code': row.get('code', row['spo']),
                                    'station': row.get('station', ''),
                                    'eoi': row.get('eoi', ''),
                                    'network': row.get('network', ''),
                                    'pollutant': pollutant,
                                    'objecttype': objecttype,
                                    'objective': obj_name,
                                    'statistic': stat,
                                    'year': year,
                                    'directive': directive,
                                    'threshold_value': threshold['value'],
                                    'threshold_operator': threshold['operator'],
                                    'measured_value': row['value'],
                                    'coverage': row.get('coverage'),
                                    'exceeded': exceeded
                                })
                        except Exception as e:
                            # Log but continue with other statistics
                            print(f"Error evaluating {stat}: {e}")
                            continue
    
    return jsonify(results), 200


@exceedances_endpoint.route('/api/data/exceedances/evaluate/regime', methods=['POST'])
@jwt_required_with_data_claim()
def evaluate_regime():
    """
    Evaluate a single assessment regime.
    
    Request Body:
        {
            "regime_id": "NO_OSLO_NO2_LV_ANNUAL",
            "year": 2023,
            "directive": "2024/2881"
        }
    
    Returns:
        JSON object with exceedance evaluation result
    
    Example:
        POST /api/data/exceedances/evaluate/regime
        {
            "regime_id": "NO_OSLO_NO2_LV_ANNUAL",
            "year": 2023,
            "directive": "2024/2881"
        }
    """
    try:
        model = ExceedancesRegimeModel(**request.json)
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    
    with CursorFromPool() as cursor:
        exc = Exceedances(cursor)
        result = exc.evaluate_regime(
            model.regime_id,
            model.year,
            model.directive
        )
    
    return jsonify(result), 200


@exceedances_endpoint.route('/api/data/exceedances/years', methods=['GET'])
@jwt_required_with_data_claim()
def get_years():
    """
    Get available years from zones data.
    Falls back to sampling_points data if no zones exist.
    
    Returns:
        JSON array of unique years
    
    Example:
        GET /api/data/exceedances/years
    """
    with CursorFromPool() as cursor:
        # First try to get years from zones
        cursor.execute("""
            SELECT DISTINCT year
            FROM zones
            ORDER BY year DESC
        """)
        
        years = [row['year'] for row in cursor.fetchall()]
        
        # If no zones exist, fall back to years from sampling points
        if not years:
            cursor.execute("""
                SELECT 
                    EXTRACT(YEAR FROM MIN(from_time))::integer as min_year,
                    EXTRACT(YEAR FROM MAX(to_time))::integer as max_year
                FROM sampling_points
                WHERE from_time IS NOT NULL 
                AND to_time IS NOT NULL
            """)
            result = cursor.fetchone()
            
            if result and result['min_year'] and result['max_year']:
                # Generate list of years between min and max
                years = list(range(result['max_year'], result['min_year'] - 1, -1))
    
    return jsonify(years), 200
