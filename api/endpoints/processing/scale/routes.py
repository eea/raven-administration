from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query import Q
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

        cursor.execute("""
            select
              id,
              zero_point::DOUBLE PRECISION,
              span_value::DOUBLE PRECISION,
              gas_concentration::DOUBLE PRECISION, 
              to_char(timestamp, 'YYYY-MM-DD HH24:MI') as timestamp,
              createdby,
              sampling_point_id
            from scaling_points
            where sampling_point_id = %(sampling_point_id)s
            order by timestamp
        """, model)
        convertions = cursor.fetchall()
        return jsonify(convertions)


@scale_endpoint.route("/api/processing/scale/scaling_points/update", methods=['POST'])
@jwt_required_with_processing_claim()
def update():
    with CursorFromPool() as cursor:
        model = UpdateModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        model.createdby = get_name()
        current_timestamp = model.current_timestamp if model.current_timestamp is not None else model.timestamp

        values = Scaling.ReScale(cursor, True, model.sampling_point_id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, current_timestamp)

        if len(values[values["verification_flag"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        values = Importing.process_scaled_values(cursor, values, False)

        rows = Helper.editScalingPoint(cursor, model.id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.createdby, values.to_dict("records"))

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

        values = Scaling.ReScale(cursor, True, model.sampling_point_id, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.timestamp)

        if len(values[values["verification_flag"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        values = Importing.process_scaled_values(cursor, values, False)
        rows = Helper.addScalingPoint(cursor, model.zero_point, model.span_value, model.gas_concentration, model.timestamp, model.sampling_point_id, model.createdby, values.to_dict("records"))

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

        if len(values[values["verification_flag"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        values = Importing.process_scaled_values(cursor, values, False)
        rows = Helper.removeScalingPoint(cursor, model.id, values.to_dict("records"))

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

        hasVerifiedValues = len(values[values["verification_flag"] == 1]) > 0

        values = Importing.process_scaled_values(cursor, values, False)

        return {"message": "The data contains verified values" if hasVerifiedValues else "", "values": values.to_dict("records")}


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
                and sp.pollutant = p.uri
                and sp.timestep = t.id
                and sp.concentration = u.id
                order by s.name, p.notation, t.label
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
