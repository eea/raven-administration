from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.processing.calculate.models import InsertModel, UpdateModel, DeleteModel
from api.core.query import Q


calculate_endpoint = Blueprint("calculate", __name__)


@calculate_endpoint.route("/api/processing/calculate", methods=['GET'])
@jwt_required()
def calculate():
    with CursorFromPool() as cursor:
        cursor.execute("""
            WITH timeseries as (
                select s.name as station, s.id as sta_id, po.notation,p.id
                from stations s, sampling_points p,  eea_pollutants po
                where 1=1
                and s.id = p.station_id
                and p.pollutant = po.uri
            )
            select 	
                spo_pri.sta_id,
	            spo_pri.station,
                cs.*, 
                spo_pri.notation as primary_pollutant,
                spo_sec.notation as secondary_pollutant,
                spo_res.notation as result_pollutant
            from 
                timeseries spo_pri,
                timeseries spo_sec,
                timeseries spo_res,
                calculated_series cs
            where 1=1
            and cs.primary = spo_pri.id
            and cs.secondary = spo_sec.id
            and cs.result = spo_res.id
        """)
        calculateions = cursor.fetchall()
        return jsonify(calculateions)


@calculate_endpoint.route("/api/processing/calculate/insert", methods=['POST'])
@jwt_required()
def calculate_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)
        sql = """ 
            insert into calculated_series ("primary", secondary, "result", "operator") 
            values (%(primary)s,%(secondary)s,%(result)s,%(operator)s)
        """
        cursor.execute(sql, model)
        return jsonify({"success": True})


@calculate_endpoint.route("/api/processing/calculate/delete", methods=['POST'])
@jwt_required()
def calculate_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from calculated_series where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})


@calculate_endpoint.route("/api/processing/calculate/update", methods=['POST'])
@jwt_required()
def calculate_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)
        sql = """ 
            update calculated_series
            set "primary" = %(primary)s,
            secondary = %(secondary)s,
            "result" = %(result)s,
            "operator" = %(operator)s
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##


@calculate_endpoint.route("/api/processing/calculate/timeseries", methods=['GET'])
@jwt_required()
def calculate_timeseries():
    timeseries = Q.timeseries()
    return jsonify(timeseries)
