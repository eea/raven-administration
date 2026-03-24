from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.query import Q

map_endpoint = Blueprint('map', __name__)


@map_endpoint.route('/api/data/map/legend', methods=['GET'])
@jwt_required_with_data_claim()
def legend_map():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                calculation_type,
                level           AS index,
                description,
                color
            FROM aqi
            GROUP BY calculation_type, level, description, color
            ORDER BY calculation_type, level
        """)
        rows = cursor.fetchall()

    legend = {}
    for row in rows:
        calc = row["calculation_type"].lower()
        legend.setdefault(calc, []).append({
            "index":       row["index"],
            "description": row["description"],
            "color":       row["color"],
        })

    return jsonify(legend)


@map_endpoint.route('/api/data/map', methods=['GET'])
@jwt_required_with_data_claim()
def map():
    aqi_type = request.args.get('aqi_type', 'EEA').upper()
    if aqi_type not in ('LOCAL', 'EEA'):
        aqi_type = 'EEA'
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        # Only select the AQI columns for the requested type
        if aqi_type == 'LOCAL':
            aqi_level = 'COALESCE(a_local.level, 0) AS aqi'
            aqi_description = 'a_local.description AS aqi_description'
            aqi_color = 'a_local.color AS aqi_color'
            join_aqi = "LEFT JOIN aqi AS a_local ON a_local.pollutant_id = sp.pollutant_id AND a_local.timestep = sp.time_resolution_id AND a_local.calculation_type = 'LOCAL' AND a_local.range @> ROUND(NULLIF(o.value, 'NaN')::numeric)"
        else:
            aqi_level = 'COALESCE(a_eea.level, 0) AS aqi'
            aqi_description = 'a_eea.description AS aqi_description'
            aqi_color = 'a_eea.color AS aqi_color'
            join_aqi = "LEFT JOIN aqi AS a_eea ON a_eea.pollutant_id = sp.pollutant_id AND a_eea.timestep = sp.time_resolution_id AND a_eea.calculation_type = 'EEA' AND a_eea.range @> ROUND(NULLIF(o.value, 'NaN')::numeric)"
        sql = f"""
            {with_network_sql}
            SELECT
                n.name AS network,
                s.name AS name,
                s.longitude AS x,
                s.latitude AS y,
                to_char(sp.from_time, 'yyyy-mm-dd HH24:mi') AS from_time,
                to_char(sp.to_time,   'yyyy-mm-dd HH24:mi') AS to_time,
                NULLIF(o.value, 'NaN')::double precision AS value,
                o.observationvalidity_id AS validity_id,
                o.observationverification_id AS verification_id,
                COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant,
                COALESCE(NULLIF(t.notation, ''), t.label) AS timestep,
                u.notation AS unit,
        ac.notation as area_classification,
                sc.notation as station_classification,
                {aqi_level},
                {aqi_description},
                {aqi_color}
            FROM observations o
            JOIN sampling_points sp       ON o.sampling_point_id = sp.id
            JOIN eea_pollutants p         ON sp.pollutant_id     = p.id
            JOIN eea_times t              ON sp.time_resolution_id = t.id
            JOIN stations s               ON s.id                = sp.station_id
            JOIN network_access n         ON n.id                = s.network_id
            JOIN eea_concentrations u     ON sp.unit_id          = u.id
            LEFT JOIN eea_areaclassifications ac ON s.area_classification_id = ac.id
            LEFT JOIN eea_spocategory sc  ON sp.spo_category_id  = sc.id
            {join_aqi}
            WHERE o.to_time = sp.to_time
        """
        cursor.execute(sql, n_param)
        values = cursor.fetchall()

    grouped = {}
    for v in values:
        key = (v["network"], v["name"], v["x"], v["y"])
        entry = {
            "from_time":         v["from_time"],
            "to_time":           v["to_time"],
            "pollutant":         v["pollutant"],
            "timestep":          v["timestep"],
            "unit":              v["unit"],
            "station_classification": v["station_classification"],
            "validity_id":       v["validity_id"],
            "verification_id":   v["verification_id"],
            "value":             v["value"],
            "aqi":               v["aqi"],
            "aqi_description":   v["aqi_description"],
            "aqi_color":         v["aqi_color"],
        }
        if key not in grouped:
            grouped[key] = {
                "network":    v["network"],
                "name":       v["name"],
                "x":          v["x"],
                "y":          v["y"],
                "area_classification": v["area_classification"],
                "timeseries": []
            }

        # Ensure timeseries entry always has AQI fields set
        if entry["aqi"] is None:
            entry["aqi"] = 0
        if not entry["aqi_description"]:
            entry["aqi_description"] = "No data"
        if not entry["aqi_color"]:
            entry["aqi_color"] = "#cccccc"
        entry["aqi_index"] = entry["aqi"] if entry["aqi"] is not None else 0

        grouped[key]["timeseries"].append(entry)

    # Sort each group's timeseries by AQI descending, then pollutant ascending

    for group in grouped.values():
        group["timeseries"] = sorted(
            group["timeseries"],
            key=lambda x: (-(x["aqi"] or 0), x["pollutant"])
        )
        # Determine group-level AQI values, descriptions, and colors
        if group["timeseries"]:
            max_aqi = max(group["timeseries"], key=lambda x: x["aqi"] or 0)
            group["aqi"] = max_aqi["aqi"]
            group["aqi_description"] = max_aqi["aqi_description"]
            group["aqi_color"] = max_aqi["aqi_color"]
            group["aqi_index"] = max_aqi["aqi"] if max_aqi["aqi"] is not None else 0
        else:
            group["aqi"] = 0
            group["aqi_description"] = "No data"
            group["aqi_color"] = "#cccccc"
            group["aqi_index"] = 0

    # Sort groups by AQI descending
    result = sorted(grouped.values(), key=lambda g: g["aqi"], reverse=False)
    return jsonify(result)
