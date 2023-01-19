from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.observingcapabilities.models import ObservingCapabilityModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q, DeleteModel
from core.query_access import Access


observingcapabilities_endpoint = Blueprint('observingcapabilities', __name__)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities', methods=['GET'])
@jwt_required_with_management_claim()
def observingcapabilities():
    with CursorFromPool() as cursor:
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f"""
            {with_samplingpoints_sql}   
            SELECT
              oc.id,
              oc.begin_position,
              oc.end_position,
              oc.process_type as process_type_id,
              oc.result_nature as result_nature_id,
              oc.sampling_point_id,
              oc.process_id,
              oc.sample_id,
              ptv.label as process_type,
              rnv.label as result_nature
          FROM observing_capabilities oc, eea_processtypevalues ptv,eea_resultnaturevalues rnv, sampling_point_access spa
          WHERE 1=1
          AND oc.process_type = ptv.id
          AND oc.result_nature = rnv.id
          AND oc.sampling_point_id = spa.id
          ORDER BY  oc.sampling_point_id, oc.begin_position
        """, n_param)
        observingcapabilities = cursor.fetchall()
        return jsonify(observingcapabilities)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/update', methods=['POST'])
@jwt_required_with_management_claim()
def observingcapabilities_update():
    with CursorFromPool() as cursor:
        model = ObservingCapabilityModel(**request.json)

        if not Access.to_observing_capability(model.id):
            raise BadRequest("Access denied for observing capability")

        sql = """
            UPDATE observing_capabilities 
            SET 
              begin_position = %(begin_position)s,
              end_position = %(end_position)s,
              process_type = %(process_type_id)s,
              result_nature = %(result_nature_id)s,
              sampling_point_id = %(sampling_point_id)s,
              process_id = %(process_id)s,
              sample_id = %(sample_id)s
            WHERE id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/insert', methods=['POST'])
@jwt_required_with_management_claim()
def observingcapabilities_insert():
    with CursorFromPool() as cursor:
        model = ObservingCapabilityModel(**request.json)

        if not Access.to_sampling_point(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        sql = """
            INSERT INTO observing_capabilities (
              id, 
              begin_position, 
              end_position, 
              process_type, 
              result_nature, 
              sampling_point_id, 
              process_id, 
              sample_id
            )
            VALUES (
              %(id)s, 
              %(begin_position)s,
              %(end_position)s,
              %(process_type_id)s, 
              %(result_nature_id)s, 
              %(sampling_point_id)s, 
              %(process_id)s, 
              %(sample_id)s
            ) 
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/delete', methods=['POST'])
@jwt_required_with_management_claim()
def observingcapabilities_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if not Access.to_observing_capabilities(model.ids):
            raise BadRequest("Access denied for observing capability")

        rows = Q.delete("observing_capabilities", model)
        if rows == 0:
            raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

        return jsonify({"success": True})
