from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool

from api.endpoints.processing.convert.models import InsertModel, UpdateModel, DeleteModel


convert_endpoint = Blueprint("convert", __name__)


@convert_endpoint.route("/api/processing/convert", methods=['GET'])
@jwt_required()
def convert():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select 
                cs.id, cs.oc_id, cs.factor::double PRECISION as factor,
                st.id as sta_id, st.name as station, po.notation as pollutant,
                s.notation as source, cs.source as source_id, 
                t.notation as target, cs.target as target_id
            from converted_series cs, eea_concentrations s, eea_concentrations t, stations st, sampling_points p, observing_capabilities oc, eea_pollutants po
            where 1=1
            and cs.source = s.id
            and cs.target = t.id
            and cs.oc_id = oc.id
            and oc.sampling_point_id = p.id
            and p.station_id = st.id
            and oc.pollutant = po.uri
        """)
        convertions = cursor.fetchall()
        return jsonify(convertions)


@convert_endpoint.route("/api/processing/convert/insert", methods=['POST'])
@jwt_required()
def convert_insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)
        model.createdby = get_jwt_identity()
        sql = """ 
             insert into converted_series ("oc_id", "source", "target", "factor", createdby) 
            values (%(oc_id)s,%(source_id)s,%(target_id)s,%(factor)s, %(createdby)s)
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/delete", methods=['POST'])
@jwt_required()
def convert_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from converted_series where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/update", methods=['POST'])
@jwt_required()
def convert_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)
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
@jwt_required()
def convert_units():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select p.notation as label, p.id as value
            from eea_concentrations p 
            order by p.notation
        """)
        units = cursor.fetchall()
        return jsonify(units)


@convert_endpoint.route("/api/processing/convert/capabilities", methods=['GET'])
@jwt_required()
def convert_capabilities():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select s.name || ' - ' || p.notation as label, c.id as value
            from observing_capabilities c, sampling_points sp, stations s, eea_pollutants p
            where c.sampling_point_id = sp.id
            and sp.station_id = s.id
            and c.pollutant = p.uri
            order by s.name, p.notation
        """)
        units = cursor.fetchall()
        return jsonify(units)
