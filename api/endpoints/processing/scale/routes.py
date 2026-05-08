from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query import Q
from core.groups import Groups
from endpoints.processing.scale.helper import Helper
from endpoints.processing.scale.models import ScalingpointModel, UpdateModel, InsertModel, DeleteModel, PreviewModel
from core.data.processing.scaling import Scaling
from core.data.processing.importing import Importing
from core.jwt_ext_custom import jwt_required_with_processing_claim
from core.jwt_ext_custom import get_name


scale_endpoint = Blueprint('scale', __name__)


@scale_endpoint.route("/api/processing/scale/scaling_points", methods=['POST'])
@jwt_required_with_processing_claim()
def scaling_points():
    with CursorFromPool() as cursor:
        model = ScalingpointModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        # Return scaling points for this SP + all non-calculated SPs in same calculated_series
        cursor.execute("""
            WITH related AS (
                SELECT %(sp_id)s::varchar AS id
                UNION
                SELECT sp.id
                FROM calculated_series cs
                JOIN sampling_points sp ON sp.id IN (cs.primary, cs.secondary)
                WHERE (cs.primary = %(sp_id)s OR cs.secondary = %(sp_id)s)
                  AND sp.id != %(sp_id)s
                  AND NOT EXISTS (SELECT 1 FROM calculated_series cs2 WHERE cs2.result = sp.id)
            )
            SELECT
                sc.id,
                sc.zero_point::DOUBLE PRECISION,
                sc.span_value::DOUBLE PRECISION,
                sc.gas_concentration::DOUBLE PRECISION,
                to_char(sc.timestamp, 'YYYY-MM-DD HH24:MI') AS timestamp,
                sc.createdby,
                sc.sampling_point_id,
                COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant
            FROM scaling_points sc
            JOIN related r ON r.id = sc.sampling_point_id
            JOIN sampling_points sp ON sp.id = sc.sampling_point_id
            JOIN eea_pollutants p ON p.id = sp.pollutant_id
            ORDER BY sc.timestamp, sc.sampling_point_id
        """, {"sp_id": model.sampling_point_id})
        return jsonify(cursor.fetchall())


@scale_endpoint.route("/api/processing/scale/scaling_points/update", methods=['POST'])
@jwt_required_with_processing_claim()
def update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        if Groups.is_calculated(cursor, model.sampling_point_id):
            raise BadRequest("Cannot add scaling points to a calculated sampling point")

        if model.zero_point == model.span_value:
            raise BadRequest("Zero point and span value cannot be the same")

        model.createdby = get_name()
        current_timestamp = model.current_timestamp if model.current_timestamp is not None else model.timestamp

        values = Scaling.ReScale(cursor, True, model.sampling_point_id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, current_timestamp)

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        rows = Helper.editScalingPoint(cursor, model.id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.createdby, values.to_dict("records") if not values.empty else [])

        if rows == 0:
            raise BadRequest(description="Could not update.")

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/insert", methods=['POST'])
@jwt_required_with_processing_claim()
def insert():
    with CursorFromPool() as cursor:
        model = InsertModel(**request.json)
        model.createdby = get_name()

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        if Groups.is_calculated(cursor, model.sampling_point_id):
            raise BadRequest("Cannot add scaling points to a calculated sampling point")

        if model.zero_point == model.span_value:
            raise BadRequest("Zero point and span value cannot be the same")

        values = Scaling.ReScale(cursor, True, model.sampling_point_id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.timestamp)

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        rows = Helper.addScalingPoint(cursor, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.sampling_point_id, model.createdby, values.to_dict("records") if not values.empty else [])

        if rows == 0:
            raise BadRequest(description="Could not insert.")

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sp = Helper.getScalingPoint(cursor, model.id)

        if Q.has_no_access(sp["sampling_point_id"]):
            raise BadRequest("Access denied for samplingpoint")

        values = Scaling.ReScale(cursor, False, sp["sampling_point_id"], sp["zero_point"], sp["span_value"], sp["gas_concentration"], sp["timestamp"], sp["timestamp"])

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        rows = Helper.removeScalingPoint(cursor, model.id, values.to_dict("records") if not values.empty else [])

        if rows == 0:
            raise BadRequest(description="Could not delete.")

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/preview", methods=['POST'])
@jwt_required_with_processing_claim()
def preview():
    with CursorFromPool() as cursor:
        model = PreviewModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        model.createdby = get_name()
        current_timestamp = model.current_timestamp if model.current_timestamp is not None else model.timestamp

        values = Scaling.ReScale(cursor, True, model.sampling_point_id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, current_timestamp)

        if values.empty:
            return {"message": "No observations found in the affected time range", "values": []}

        hasVerifiedValues = len(values[values["observationverification_id"] == 1]) > 0

        values = Importing.process_scaled_values(cursor, values, False)

        return {"message": "The data contains verified values" if hasVerifiedValues else "", "values": values.to_dict("records")}


@scale_endpoint.route('/api/processing/scale/group_members', methods=['GET'])
@jwt_required_with_processing_claim()
def group_members():
    sp_id = request.args.get('sp_id')
    if not sp_id:
        raise BadRequest("sp_id required")
    with CursorFromPool() as cursor:
        # Find all non-calculated SPs that share a calculated_series with this SP
        cursor.execute("""
            SELECT DISTINCT sp.id,
                   COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant
            FROM calculated_series cs
            JOIN sampling_points sp ON sp.id IN (cs.primary, cs.secondary)
            JOIN eea_pollutants p ON p.id = sp.pollutant_id
            WHERE (cs.primary = %(sp_id)s OR cs.secondary = %(sp_id)s)
              AND sp.id != %(sp_id)s
            ORDER BY pollutant
        """, {"sp_id": sp_id})
        return jsonify(cursor.fetchall())


## LOOKUPS ##
@scale_endpoint.route('/api/processing/scale/timeseries', methods=['GET'])
@jwt_required_with_processing_claim()
def timeseries():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.networks_by_access_as_sql()
        cursor.execute(f"""
            with
            {with_network_sql},
            timeseries as (
                select CONCAT(s.name,', ', p.notation,', ', t.label, ', ', u.notation )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t, eea_concentrations u, network_access n
                where sp.station_id = s.id
                and n.id = s.network_id
                and sp.pollutant_id = p.id
                and sp.time_resolution_id = t.id
                and sp.unit_id = u.id
                and NOT EXISTS (SELECT 1 FROM calculated_series cs WHERE cs.result = sp.id)
                order by LOWER(s.name), LOWER(p.notation), LOWER(t.label)
            ),
            scaling_points_with_timeseries as (
                select distinct sampling_point_id as id from scaling_points
            )
            select t.*, case when sp.id is NULL then false else true end as hasScalingPoint
            from timeseries t
            LEFT JOIN scaling_points_with_timeseries sp
            ON t.value=sp.id
            order by hasScalingPoint desc, t.label
        """, n_param)
        timeseries = cursor.fetchall()
        return jsonify(timeseries)
