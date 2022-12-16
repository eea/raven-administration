from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.processing.convert.models import InsertModel, UpdateModel, DeleteModel
from core.query import Q
from core.jwt_ext_custom import jwt_required_with_processing_claim
from core.jwt_ext_custom import get_name

convert_endpoint = Blueprint("convert", __name__)


@convert_endpoint.route("/api/processing/convert", methods=['GET'])
@jwt_required_with_processing_claim()
def convert():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            select
                cs.id, cs.sampling_point_id, cs.factor::double PRECISION as factor,
                st.id as sta_id, st.name as station, po.notation as pollutant,
                s.notation as source, cs.source as source_id,
                t.notation as target, cs.target as target_id,
                cs.createdby, ti.label as timestep
            from converted_series cs, eea_concentrations s, eea_concentrations t, stations st, sampling_points p,  eea_pollutants po, eea_times ti, network_access n
            where 1=1
            and n.id = st.network_id
            and cs.source = s.id
            and cs.target = t.id
            and cs.sampling_point_id = p.id
            and p.station_id = st.id
            and p.pollutant = po.uri
            and p.timestep = ti.id
        """, n_param)
        convertions = cursor.fetchall()
        return jsonify(convertions)


@convert_endpoint.route("/api/processing/convert/insert", methods=['POST'])
@jwt_required_with_processing_claim()
def convert_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        model.createdby = get_name()
        sql = """ 
             insert into converted_series ("sampling_point_id", "source", "target", "factor", createdby) 
            values (%(sampling_point_id)s,%(source_id)s,%(target_id)s,%(factor)s, %(createdby)s)
        """
        cursor.execute(sql, model)
        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def convert_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if __has_no_access(model.id):
            raise BadRequest("Access denied for samplingpoint")

        sql = "delete from converted_series where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/update", methods=['POST'])
@jwt_required_with_processing_claim()
def convert_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)

        if __has_no_access(model.id):
            raise BadRequest("Access denied for samplingpoint")

        sql = """ 
            update converted_series
            set "source" = %(source_id)s,
            "target" = %(target_id)s,
            "factor" = %(factor)s
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##

@convert_endpoint.route("/api/processing/convert/units", methods=['GET'])
@jwt_required_with_processing_claim()
def convert_units():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select p.notation as label, p.id as value
            from eea_concentrations p 
            order by p.notation
        """)
        units = cursor.fetchall()
        return jsonify(units)


@convert_endpoint.route("/api/processing/convert/timeseries", methods=['GET'])
@jwt_required_with_processing_claim()
def convert_timeseries():
    timeseries = Q.timeseries_by_access()
    return jsonify(timeseries)


def __has_no_access(id):
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        sql = f""" 
            {with_network_sql}
            select 1 from converted_series cs, sampling_points sp, stations s, network_access n
            where cs.id = %(id)s
            and cs.sampling_point_id = sp.id
            and sp.station_id = s.id
            and s.network_id = n.id
        """
        cursor.execute(sql, {"id": id, "networkids": n_param["networkids"]})
        row = cursor.fetchall()
        return len(row) == 0
