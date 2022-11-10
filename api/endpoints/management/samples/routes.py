from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.samples.models import SampleModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_observations_claim


samples_endpoint = Blueprint('samples', __name__)


@samples_endpoint.route('/api/management/samples', methods=['GET'])
@jwt_required_with_observations_claim()
def samples():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT * FROM samples ORDER BY id asc")
        samples = cursor.fetchall()
        return jsonify(samples)


@samples_endpoint.route('/api/management/samples/update', methods=['POST'])
@jwt_required_with_observations_claim()
def samples_update():
    with CursorFromPool() as cursor:
        model = SampleModel(**request.json)
        sql = """ 
            UPDATE samples 
            SET 
              inlet_height = %(inlet_height)s,
  			      building_distance = %(building_distance)s,
	      		  kerb_distance = %(kerb_distance)s
            WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@samples_endpoint.route('/api/management/samples/insert', methods=['POST'])
@jwt_required_with_observations_claim()
def samples_insert():
    with CursorFromPool() as cursor:
        model = SampleModel(**request.json)
        sql = """
            INSERT INTO samples (id, inlet_height, building_distance, kerb_distance)
            VALUES (%(id)s, %(inlet_height)s, %(building_distance)s, %(kerb_distance)s) 
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@samples_endpoint.route('/api/management/samples/delete', methods=['POST'])
@jwt_required_with_observations_claim()
def samples_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = """
          delete from samples where id = %(id)s 
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
