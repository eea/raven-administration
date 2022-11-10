from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.observingcapabilities.models import ObservingCapabilityModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_observations_claim


observingcapabilities_endpoint = Blueprint('observingcapabilities', __name__)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities', methods=['GET'])
@jwt_required_with_observations_claim()
def observingcapabilities():
    with CursorFromPool() as cursor:
        cursor.execute("""
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
          FROM observing_capabilities oc, eea_processtypevalues ptv,eea_resultnaturevalues rnv
          WHERE 1=1
          AND oc.process_type = ptv.id
          AND oc.result_nature = rnv.id
          ORDER BY  oc.sampling_point_id, oc.begin_position
        """)
        observingcapabilities = cursor.fetchall()
        return jsonify(observingcapabilities)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/update', methods=['POST'])
@jwt_required_with_observations_claim()
def observingcapabilities_update():
    with CursorFromPool() as cursor:
        model = ObservingCapabilityModel(**request.json)
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
@jwt_required_with_observations_claim()
def observingcapabilities_insert():
    with CursorFromPool() as cursor:
        model = ObservingCapabilityModel(**request.json)
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
@jwt_required_with_observations_claim()
def observingcapabilities_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from observing_capabilities where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
