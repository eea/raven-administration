from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.processing.autovalidate.models import InsertModel, UpdateModel
from core.jwt_ext_custom import jwt_required_with_processing_claim
from core.query import Q, DeleteModel

autovalidate_endpoint = Blueprint("autovalidate", __name__)


@autovalidate_endpoint.route("/api/processing/autovalidate", methods=['GET'])
@jwt_required_with_processing_claim()
def autovalidate():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select v.id, v.min, v.max, v.rep, v.enabled, p.notation as pollutant, p.id as pollutant_id
            from autovalidated_series v, eea_pollutants p
            where v.pollutant_id = p.id
            order by p.notation
        """)
        autovalidations = cursor.fetchall()
        return jsonify(autovalidations)


@autovalidate_endpoint.route("/api/processing/autovalidate/insert", methods=['POST'])
@jwt_required_with_processing_claim()
def autovalidate_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)
        sql = """ 
            insert into autovalidated_series ("min", "max", rep, pollutant_id) 
            values (%(min)s, %(max)s, %(rep)s, %(pollutant_id)s)
        """
        cursor.execute(sql, model)
        return jsonify({"success": True})


@autovalidate_endpoint.route("/api/processing/autovalidate/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def autovalidate_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("autovalidated_series", model)

    if rows == 0:
        raise BadRequest("Could not delete for ids " + ','.join(map(str, model.ids)))

    return jsonify({"success": True})


@autovalidate_endpoint.route("/api/processing/autovalidate/update", methods=['POST'])
@jwt_required_with_processing_claim()
def autovalidate_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)
        sql = """ 
            update autovalidated_series
            set min = %(min)s, max = %(max)s, rep = %(rep)s  
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##

@autovalidate_endpoint.route("/api/processing/autovalidate/pollutants", methods=['GET'])
@jwt_required_with_processing_claim()
def autovalidate_pollutants():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT pollutant_id FROM autovalidated_series")
        existing = [row["pollutant_id"] for row in cursor.fetchall()]
    return jsonify(Q.pollutants_lookup(exclude_ids=existing if existing else None))
