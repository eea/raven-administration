from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.attainments.models import AttainmentModel, GenerateModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core.eea.generate_attainment.g import generate


attainments_endpoint = Blueprint('attainments', __name__)


@attainments_endpoint.route('/api/management/attainments', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def attainments():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select 
            a.id,
            a.name,
            ar.name as assessment_regime,
            a.assessmentregime_id as assessment_regime_id,
            a.comment ,
            count(e.id) as ed_count
          from assessmentregimes ar, attainments a left join exceedancedescriptions e on a.id = e.attainment_id
          where a.assessmentregime_id = ar.id
          group by
            a.id,
            a.name,
            ar.name ,
            a.assessmentregime_id ,
            a.comment
          order by name
        """)
        assessmentregimes = cursor.fetchall()
        return jsonify(assessmentregimes)


@attainments_endpoint.route('/api/management/attainments/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def attainments_update():
    with CursorFromPool() as cursor:
        model = AttainmentModel(**request.json)

        # Update assessment regime
        sql = """            
          UPDATE attainments 
          SET 
            name=%(name)s,
            assessmentregime_id=%(assessment_regime_id)s,
            comment=%(comment)s
          WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@attainments_endpoint.route('/api/management/attainments/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def attainments_insert():
    with CursorFromPool() as cursor:
        model = AttainmentModel(**request.json)
        sql = """
            insert into attainments (
                id, 
                name, 
                assessmentregime_id, 
                comment
            )
            values (
                %(id)s, 
                %(name)s, 
                %(assessment_regime_id)s, 
                %(comment)s
            )             
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@attainments_endpoint.route("/api/management/attainments/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def attainments_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("attainments", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})
    return jsonify({"success": True})


@attainments_endpoint.route('/api/management/attainments/generate', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def attainments_generate():
    model = GenerateModel(**request.json)
    generate(model["year"], model["deleteExistingAttainments"])
    return jsonify({"success": True})
