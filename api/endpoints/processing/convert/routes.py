from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.processing.convert.models import InsertModel, UpdateModel
from core.query import Q, DeleteModel
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
                sp_unit.notation as target,
                cs.createdby, ti.label as timestep
            from converted_series cs
            join eea_concentrations s on cs.source = s.id
            join sampling_points p on cs.sampling_point_id = p.id
            join eea_concentrations sp_unit on p.unit_id = sp_unit.id
            join stations st on p.station_id = st.id
            join eea_pollutants po on p.pollutant_id = po.id
            join eea_times ti on p.time_resolution_id = ti.id
            join network_access n on n.id = st.network_id
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

        # Validate source unit is different from sampling point's unit
        cursor.execute("SELECT unit_id FROM sampling_points WHERE id = %(sampling_point_id)s", model)
        sp = cursor.fetchone()
        if sp and sp["unit_id"] == model.source_id:
            raise BadRequest("Source unit cannot be the same as the sampling point's unit")

        model.createdby = get_name()
        sql = """ 
            INSERT INTO converted_series (sampling_point_id, source, target, factor, createdby) 
            SELECT %(sampling_point_id)s, %(source_id)s, sp.unit_id, %(factor)s, %(createdby)s
            FROM sampling_points sp
            WHERE sp.id = %(sampling_point_id)s
        """
        cursor.execute(sql, model)
        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def convert_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        # Get the first (and only) ID from the array
        convert_id = model.ids[0] if model.ids else None
        if not convert_id:
            raise BadRequest("No conversion ID provided")

        if __has_no_access(convert_id):
            raise BadRequest("Access denied for samplingpoint")

        sql = "delete from converted_series where id = %(id)s"
        cursor.execute(sql, {"id": convert_id})
        if cursor.rowcount == 0:
            raise BadRequest(f"Could not delete conversion {convert_id}")

        return jsonify({"success": True})


@convert_endpoint.route("/api/processing/convert/update", methods=['POST'])
@jwt_required_with_processing_claim()
def convert_update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)

        if __has_no_access(model.id):
            raise BadRequest("Access denied for samplingpoint")

        sql = """ 
            UPDATE converted_series
            SET source = %(source_id)s,
                factor = %(factor)s
            WHERE id = %(id)s
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
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            SELECT CONCAT(s.name, ', ', p.notation, ', ', t.label, ', ', u.notation) as label, 
                   sp.id as value,
                   u.id as unit_id
            FROM sampling_points sp
            JOIN stations s ON sp.station_id = s.id
            JOIN network_access n ON n.id = s.network_id
            JOIN eea_pollutants p ON sp.pollutant_id = p.id
            JOIN eea_times t ON sp.time_resolution_id = t.id
            JOIN eea_concentrations u ON sp.unit_id = u.id
            WHERE sp.id NOT IN (SELECT sampling_point_id FROM converted_series)
            ORDER BY LOWER(s.name), p.notation, t.label
        """, n_param)
        return jsonify(cursor.fetchall())


@convert_endpoint.route("/api/processing/convert/download", methods=['GET'])
@jwt_required_with_processing_claim()
def convert_download():
    """Download conversions as CSV"""
    from core.utils import download_csv

    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            select
                st.name as station, po.notation as pollutant, ti.label as timestep,
                s.notation as source,
                t.notation as target,
                cs.factor::double PRECISION as factor
            from converted_series cs, eea_concentrations s, eea_concentrations t, stations st, sampling_points p,  eea_pollutants po, eea_times ti, network_access n
            where 1=1
            and n.id = st.network_id
            and cs.source = s.id
            and cs.target = t.id
            and cs.sampling_point_id = p.id
            and p.station_id = st.id
            and p.pollutant_id = po.id
            and p.time_resolution_id = ti.id
            order by LOWER(st.name), po.notation, ti.label
        """, n_param)
        conversions = cursor.fetchall()
        return download_csv(conversions, "conversions.csv")


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
