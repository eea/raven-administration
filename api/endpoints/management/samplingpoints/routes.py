from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.samplingpoints.models import SamplingPointsModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q, DeleteModel, vocab_option
from core.query_access import Access


samplingpoints_endpoint = Blueprint('samplingpoints', __name__)


@samplingpoints_endpoint.route('/api/management/samplingpoints', methods=['GET'])
@jwt_required_with_management_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f"""        
            {with_samplingpoints_sql}
            SELECT
              sp.id,
              sp.sampling_point_reference_id,
              to_char(sp.from_time, 'YYYY-MM-DD HH24:MI') as from_time,
              to_char(sp.to_time,   'YYYY-MM-DD HH24:MI') as to_time,
              sp.inlet_height,
              sp.building_distance,
              sp.kerb_distance,
              sp.emission_source_distance,
              sp.hotspot,
              sp.logger_id,
              sp.private,
              sp.use_in_public_api,
              sp.daily_check,
              sp.pollutant_id, COALESCE(NULLIF(p.notation, ''), p.label) as pollutant,
              sp.time_resolution_id, COALESCE(NULLIF(tr.notation, ''), tr.label) as time_resolution,
              sp.unit_id, u.notation as unit,
              sp.station_id, st.name as station,
              sp.sampling_point_category_id, sc.label as sampling_point_category
          FROM
              sampling_points sp
              LEFT JOIN eea_pollutants p ON sp.pollutant_id = p.id
              LEFT JOIN eea_times tr ON sp.time_resolution_id = tr.id
              LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
              LEFT JOIN eea_spocategory sc ON sp.sampling_point_category_id = sc.id
              INNER JOIN stations st ON sp.station_id = st.id
              INNER JOIN sampling_point_access spa ON sp.id = spa.id
          ORDER BY LOWER(st.name), COALESCE(NULLIF(p.notation, ''), p.label)
        """, n_param)
        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@samplingpoints_endpoint.route('/api/management/samplingpoints/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def samplingpoints_lookups():
    with CursorFromPool() as cursor:
        # Get stations accessible to user
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            SELECT st.id as value, st.name as label
            FROM stations st
            INNER JOIN networks n ON st.network_id = n.id
            INNER JOIN network_access na ON n.id = na.id
            ORDER BY LOWER(st.name)
        """, n_param)
        stations = cursor.fetchall()
        
        pollutants = Q.pollutants_lookup()
        
        # Both lists show 'notation — label': the notation alone is not enough to pick from.
        # 80 unit notations are near-indistinguishable (mg/m3, mg/l, mg/m3.h, mgS.m-1), and
        # eea_times carries two rows with the same notation. See core.query.vocab_option.
        cursor.execute(f"SELECT id as value, {vocab_option()} as label FROM eea_times "
                       f"ORDER BY LOWER(notation), LOWER(label)")
        time_resolutions = cursor.fetchall()

        cursor.execute(f"SELECT id as value, {vocab_option()} as label FROM eea_concentrations "
                       f"ORDER BY LOWER(notation), LOWER(label)")
        units = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_spocategory ORDER BY LOWER(label)")
        sampling_point_categories = cursor.fetchall()

        return jsonify({
            "stations": stations,
            "pollutants": pollutants,
            "time_resolutions": time_resolutions,
            "units": units,
            "sampling_point_categories": sampling_point_categories
        })


@samplingpoints_endpoint.route('/api/management/samplingpoints/update', methods=['POST'])
@jwt_required_with_management_claim()
def samplingpoints_update():
    with CursorFromPool() as cursor:
        model = SamplingPointsModel(**request.json)

        if not Access.to_sampling_point(model.id):
            raise BadRequest("Access denied for samplingpoint")

        sql = """ 
          UPDATE sampling_points
          SET
            sampling_point_reference_id=%(sampling_point_reference_id)s,
            from_time=%(from_time)s::timestamp,
            to_time=%(to_time)s::timestamp,
            inlet_height=%(inlet_height)s,
            building_distance=%(building_distance)s,
            kerb_distance=%(kerb_distance)s,
            emission_source_distance=%(emission_source_distance)s,
            hotspot=%(hotspot)s,
            logger_id=%(logger_id)s,
            private=%(private)s,
            use_in_public_api=%(use_in_public_api)s,
            daily_check=%(daily_check)s,
            pollutant_id=%(pollutant_id)s,
            time_resolution_id=%(time_resolution_id)s,
            unit_id=%(unit_id)s,
            station_id=%(station_id)s,
            sampling_point_category_id=%(sampling_point_category_id)s
          WHERE id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"msg": "Sampling point updated successfully"})


@samplingpoints_endpoint.route('/api/management/samplingpoints/insert', methods=['POST'])
@jwt_required_with_management_claim()
def samplingpoints_insert():
    with CursorFromPool() as cursor:
        model = SamplingPointsModel(**request.json)

        if not Access.to_station(model.station_id):
            raise BadRequest("Access denied for station")

        sql = """
          INSERT INTO sampling_points (
            id, sampling_point_reference_id, from_time, to_time,
            inlet_height, building_distance, kerb_distance,
            emission_source_distance, hotspot, logger_id, private, use_in_public_api, daily_check,
            pollutant_id, time_resolution_id, unit_id, station_id, sampling_point_category_id
          )
          VALUES (
            %(id)s, %(sampling_point_reference_id)s, %(from_time)s::timestamp, %(to_time)s::timestamp,
            %(inlet_height)s, %(building_distance)s, %(kerb_distance)s,
            %(emission_source_distance)s, %(hotspot)s, %(logger_id)s, %(private)s, %(use_in_public_api)s, %(daily_check)s,
            %(pollutant_id)s, %(time_resolution_id)s, %(unit_id)s, %(station_id)s, %(sampling_point_category_id)s
          )
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"msg": "Sampling point created successfully"})


@samplingpoints_endpoint.route('/api/management/samplingpoints/delete', methods=['POST'])
@jwt_required_with_management_claim()
def samplingpoints_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if not Access.to_sampling_points(model.ids):
            raise BadRequest("Access denied for samplingpoint")

        rows = Q.delete("sampling_points", model)
        if rows == 0:
            raise BadRequest("Could not delete for ids " + ','.join(model.ids))

        return jsonify({"msg": "Sampling point deleted successfully"})
