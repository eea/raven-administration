from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.samplingpoints.models import SamplingPointsModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q, DeleteModel
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
              sp.inlet_height,
              sp.building_distance,
              sp.kerb_distance,
              sp.emission_source_distance,
              sp.logger_id,
              sp.private,
              sp.use_in_public_api,
              sp.pollutant_id, COALESCE(NULLIF(p.notation, ''), p.label) as pollutant,
              sp.time_resolution_id, COALESCE(NULLIF(tr.notation, ''), tr.label) as time_resolution,
              sp.unit_id, u.notation as unit,
              sp.station_id, st.name as station,
              sp.spo_category_id, sc.label as spo_category
          FROM
              sampling_points sp
              LEFT JOIN eea_pollutants p ON sp.pollutant_id = p.id
              LEFT JOIN eea_times tr ON sp.time_resolution_id = tr.id
              LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
              LEFT JOIN eea_spocategory sc ON sp.spo_category_id = sc.id
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
        
        cursor.execute("SELECT id as value, COALESCE(NULLIF(notation, ''), label) as label FROM eea_times ORDER BY COALESCE(NULLIF(notation, ''), label)")
        time_resolutions = cursor.fetchall()
        
        cursor.execute("SELECT id as value, notation as label FROM eea_concentrations ORDER BY LOWER(notation)")
        units = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_spocategory ORDER BY LOWER(label)")
        spocategories = cursor.fetchall()
        
        return jsonify({
            "stations": stations,
            "pollutants": pollutants,
            "time_resolutions": time_resolutions,
            "units": units,
            "spocategories": spocategories
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
            inlet_height=%(inlet_height)s,
            building_distance=%(building_distance)s,
            kerb_distance=%(kerb_distance)s,
            emission_source_distance=%(emission_source_distance)s,
            logger_id=%(logger_id)s,
            private=%(private)s,
            use_in_public_api=%(use_in_public_api)s,
            pollutant_id=%(pollutant_id)s,
            time_resolution_id=%(time_resolution_id)s,
            unit_id=%(unit_id)s,
            station_id=%(station_id)s,
            spo_category_id=%(spo_category_id)s
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
            id, inlet_height, building_distance, kerb_distance,
            emission_source_distance, logger_id, private, use_in_public_api,
            pollutant_id, time_resolution_id, unit_id, station_id, spo_category_id
          )
          VALUES (
            %(id)s, %(inlet_height)s, %(building_distance)s, %(kerb_distance)s,
            %(emission_source_distance)s, %(logger_id)s, %(private)s, %(use_in_public_api)s,
            %(pollutant_id)s, %(time_resolution_id)s, %(unit_id)s, %(station_id)s, %(spo_category_id)s
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
            raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

        return jsonify({"msg": "Sampling point deleted successfully"})
