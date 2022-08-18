from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool

from api.endpoints.processing.calculate.models import InsertModel, UpdateModel, DeleteModel


calculate_endpoint = Blueprint("calculate", __name__)


@calculate_endpoint.route("/api/processing/calculate", methods=['GET'])
@jwt_required()
def calculate():
    with CursorFromPool() as cursor:
        cursor.execute("""
            WITH timeseries as (
                select s.name as station, s.id as sta_id, po.notation, oc.id
                from stations s, sampling_points p, observing_capabilities oc, eea_pollutants po
                where 1=1
                and s.id = p.station_id
                and p.id = oc.sampling_point_id
                and oc.pollutant = po.uri 
            )
            select 	
                oc_pri.sta_id,
	            oc_pri.station,
                cs.*, 
                oc_pri.notation as primary_pollutant,
                oc_sec.notation as secondary_pollutant,
                oc_res.notation as result_pollutant
            from 
                timeseries oc_pri, 
                timeseries oc_sec, 
                timeseries oc_res, 
                calculated_series cs
            where 1=1
            and cs.primary = oc_pri.id
            and cs.secondary = oc_sec.id
            and cs.result = oc_res.id
        """)
        calculateions = cursor.fetchall()
        return jsonify(calculateions)


@calculate_endpoint.route("/api/processing/calculate/insert", methods=['POST'])
@jwt_required()
def calculate_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)
        model.createdby = get_jwt_identity()
        sql = """ 
            insert into calculated_series ("primary", secondary, "result", "operator", createdby) 
            values (%(primary)s,%(secondary)s,%(result)s,%(operator)s, %(createdby)s)
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

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


@calculate_endpoint.route("/api/processing/calculate/capabilities", methods=['GET'])
@jwt_required()
def calculate_capabilities():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select s.name || ' - ' || p.notation as label, c.id as value
            from observing_capabilities c, sampling_points sp, stations s, eea_pollutants p
            where c.sampling_point_id = sp.id
            and sp.station_id = s.id
            and c.pollutant = p.uri
            order by s.name, p.notation
        """)
        timeseries = cursor.fetchall()
        return jsonify(timeseries)
