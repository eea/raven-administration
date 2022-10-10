from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool

from api.endpoints.management.observingcapabilities.models import ObservingCapabilityModel, DeleteModel


observingcapabilities_endpoint = Blueprint('observingcapabilities', __name__)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities', methods=['GET'])
@jwt_required()
def observingcapabilities():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT 
                oc.id,
                oc.begin_position,
                oc.end_position,
                oc.process_type,
                oc.result_nature,
                oc.sampling_point_id,
                oc.process_id,
                oc.sample_id,
                ptv.label as process_type_name,
                rnv.label as result_nature_name
            FROM observing_capabilities oc
                left join sampling_points sp on oc.sampling_point_id = sp.id
                left join eea_processtypevalues ptv on lower(oc.process_type) = lower(ptv.id)
                left join eea_resultnaturevalues rnv on lower(oc.result_nature) = lower(rnv.id)

        """)
        observingcapabilities = cursor.fetchall()
        return jsonify(observingcapabilities)


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/update', methods=['POST'])
@jwt_required()
def observingcapabilities_update():
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
                sample_id)
            VALUES (
                %(id)s, 
                %(begin_position)s,
                %(end_position)s,
                %(process_type)s, 
                %(result_nature)s, 
                %(sampling_point_id)s, 
                %(process_id)s, 
                %(sample_id)s)

            ON CONFLICT (id) DO 
            UPDATE SET begin_position=%(begin_position)s,
              end_position=%(end_position)s,
              process_type=%(process_type)s,
              result_nature=%(result_nature)s,
              sampling_point_id=%(sampling_point_id)s,
              process_id=%(process_id)s,
              sample_id=%(sample_id)s

        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@observingcapabilities_endpoint.route('/api/management/observingcapabilities/delete', methods=['POST'])
@jwt_required()
def observingcapabilities_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = """
          delete from observing_capabilities where id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
