from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.processing.calculate.models import InsertModel, UpdateModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_processing_claim


calculate_endpoint = Blueprint("calculate", __name__)


@calculate_endpoint.route("/api/processing/calculate", methods=['GET'])
@jwt_required_with_processing_claim()
def calculate():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql},            
            timeseries as (
                select s.name as station, s.id as sta_id, po.notation,p.id
                from stations s, sampling_points p,  eea_pollutants po, network_access n
                where 1=1
                and s.network_id = n.id
                and s.id = p.station_id
                and p.pollutant_id = po.id
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
        """, n_param)
        calculateions = cursor.fetchall()
        return jsonify(calculateions)


@calculate_endpoint.route("/api/processing/calculate/insert", methods=['POST'])
@jwt_required_with_processing_claim()
def calculate_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)

        if Q.any_has_no_access([model.primary, model.secondary, model.result]):
            raise BadRequest("Access denied for samplingpoint")

        sql = """ 
            insert into calculated_series ("primary", secondary, "result", "operator") 
            values (%(primary)s,%(secondary)s,%(result)s,%(operator)s)
        """
        cursor.execute(sql, model)
        return jsonify({"success": True})


@calculate_endpoint.route("/api/processing/calculate/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def calculate_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        # Get the first (and only) ID from the array
        calc_id = model.ids[0] if model.ids else None
        if not calc_id:
            raise BadRequest("No calculation ID provided")

        sampling_point_ids = __get_sampling_points_from_id(calc_id)

        if Q.any_has_no_access(sampling_point_ids):
            raise BadRequest("Access denied for samplingpoint")

        sql = "delete from calculated_series where id = %(id)s"
        cursor.execute(sql, {"id": calc_id})
        if cursor.rowcount == 0:
            raise BadRequest(f"Could not delete calculation {calc_id}")

        return jsonify({"success": True})


@calculate_endpoint.route("/api/processing/calculate/update", methods=['POST'])
@jwt_required_with_processing_claim()
def calculate_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)

        if Q.any_has_no_access([model.primary, model.secondary, model.result]):
            raise BadRequest("Access denied for samplingpoint")

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
@jwt_required_with_processing_claim()
def calculate_timeseries():
    timeseries = Q.timeseries_by_access()
    return jsonify(timeseries)


@calculate_endpoint.route("/api/processing/calculate/download", methods=['GET'])
@jwt_required_with_processing_claim()
def calculate_download():
    """Download calculations as CSV"""
    from core.utils import download_csv

    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql},            
            timeseries as (
                select s.name as station, s.id as sta_id, po.notation,p.id
                from stations s, sampling_points p,  eea_pollutants po, network_access n
                where 1=1
                and s.network_id = n.id
                and s.id = p.station_id
                and p.pollutant_id = po.id
            )
            select 	
	              spo_pri.station,
                spo_pri.notation as primary_pollutant,
                cs.operator,
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
            order by spo_pri.station, spo_pri.notation
        """, n_param)
        calculations = cursor.fetchall()
        return download_csv(calculations, "calculations.csv")


def __get_sampling_points_from_id(id):
    with CursorFromPool() as cursor:
        sql = f""" 
            select ARRAY[cs.primary, cs.secondary,cs.result] as spid
            from calculated_series cs
            where cs.id =  %(id)s
        """
        cursor.execute(sql, {"id": id})
        row = cursor.fetchone()
        return tuple(row["spid"])
