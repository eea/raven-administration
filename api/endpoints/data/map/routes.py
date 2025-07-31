from flask import jsonify, Blueprint
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.query import Q
from core.aqi import get_aqi, get_aqi_legend
map_endpoint = Blueprint('map', __name__)


@map_endpoint.route('/api/data/map/legend', methods=['GET'])
def legend_map():
    return jsonify(get_aqi_legend())


@map_endpoint.route('/api/data/map', methods=['GET'])
@jwt_required_with_data_claim()
def map():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        sql = f"""
          {with_network_sql}
          select
            n.name as network,
            s.name as name,
            st_x(geom) as x,
            st_y(geom) as y,
            to_char(sp.from_time,'yyyy-mm-dd HH24:mi') as from_time,
            to_char(sp.to_time,'yyyy-mm-dd HH24:mi') as to_time,
            o.value::double precision as value,
            o.validation_flag,
            o.verification_flag,
            p.notation as pollutant,
            t.label as timestep,
            u.notation as unit
          from observations o
          join sampling_points sp on o.sampling_point_id = sp.id
          join eea_pollutants p on sp.pollutant = p.uri
          join eea_times t on sp.timestep = t.id
          join stations s on s.id = sp.station_id
          join network_access n on n.id = s.network_id
          join eea_concentrations u on sp.concentration = u.id
          where o.to_time = sp.to_time
        """
        cursor.execute(sql, n_param)
        values = cursor.fetchall()

        # Group by network, station, x, y
        grouped = {}
        for v in values:
            key = (v["network"], v["name"], v["x"], v["y"])
            timeseries_entry = {
                "from_time": v["from_time"],
                "pollutant": v["pollutant"],
                "timestep": v["timestep"],
                "to_time": v["to_time"],
                "unit": v["unit"],
                "validation_flag": v["validation_flag"],
                "value": v["value"],
                "verification_flag": v["verification_flag"],
            }
            aqi_info = get_aqi(v["pollutant"], v["value"], v["timestep"])
            timeseries_entry["aqi"] = aqi_info["index"]
            timeseries_entry["aqi_description"] = aqi_info["description"]
            timeseries_entry["aqi_color"] = aqi_info["color"]

            if key not in grouped:
                grouped[key] = {
                    "network": v["network"],
                    "name": v["name"],
                    "x": v["x"],
                    "y": v["y"],
                    "timeseries": []
                }
            grouped[key]["timeseries"].append(timeseries_entry)

        # Sort timeseries by AQI descending, then pollutant name ascending for each group
        for group in grouped.values():
            group["timeseries"] = sorted(
                group["timeseries"],
                key=lambda x: (-x["aqi"], x["pollutant"])
            )
            # Find the timeseries entry with the highest AQI index
            if group["timeseries"]:
                max_aqi_entry = max(group["timeseries"], key=lambda x: x["aqi"])
                group["aqi"] = max_aqi_entry["aqi"]
                group["aqi_description"] = max_aqi_entry["aqi_description"]
            else:
                group["aqi"] = 0
                group["aqi_description"] = "No data"

        result = list(grouped.values())
        return jsonify(result)
