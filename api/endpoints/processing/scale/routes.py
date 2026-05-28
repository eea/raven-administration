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
from core.log_context import set_log_context
import pandas as pd


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
        items = request.json if isinstance(request.json, list) else [request.json]
        models = [UpdateModel(**item) for item in items]
        createdby = get_name()

        for m in models:
            if Q.has_no_access(m.sampling_point_id):
                raise BadRequest("Access denied for samplingpoint")
            if Groups.is_calculated(cursor, m.sampling_point_id):
                raise BadRequest("Cannot add scaling points to a calculated sampling point")
            if m.zero_point == m.span_value:
                raise BadRequest("Zero point and span value cannot be the same")

        old_timestamp = models[0].current_timestamp or models[0].timestamp
        scalingpoints_list = [
            {"sampling_point_id": m.sampling_point_id, "zero_point": m.zero_point, "span_value": m.span_value, "gas_concentration": m.gas_concentration, "timestamp": m.timestamp}
            for m in models
        ]

        values = Scaling.ReScale(cursor, scalingpoints_list, use_scalingpoint=True, old_timestamp=old_timestamp)

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        for m in models:
            if m.id:
                rows = Helper._updateScalingPoint(cursor, m.id, m.zero_point, m.span_value, m.gas_concentration, m.timestamp, createdby)
                if rows == 0:
                    raise BadRequest(description=f"Could not update scaling point {m.id}.")
            else:
                Helper._insertScalingPoint(cursor, m.zero_point, m.span_value, m.gas_concentration, m.timestamp, m.sampling_point_id, createdby)

        if not values.empty:
            set_log_context(cursor, 'scaling')
            Helper._insertScaledValues(cursor, values.to_dict("records"))

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/insert", methods=['POST'])
@jwt_required_with_processing_claim()
def insert():
    with CursorFromPool() as cursor:
        items = request.json if isinstance(request.json, list) else [request.json]
        models = [InsertModel(**item) for item in items]
        createdby = get_name()

        for m in models:
            if Q.has_no_access(m.sampling_point_id):
                raise BadRequest("Access denied for samplingpoint")
            if Groups.is_calculated(cursor, m.sampling_point_id):
                raise BadRequest("Cannot add scaling points to a calculated sampling point")
            if m.zero_point == m.span_value:
                raise BadRequest("Zero point and span value cannot be the same")

        scalingpoints_list = [
            {"sampling_point_id": m.sampling_point_id, "zero_point": m.zero_point, "span_value": m.span_value, "gas_concentration": m.gas_concentration, "timestamp": m.timestamp}
            for m in models
        ]

        values = Scaling.ReScale(cursor, scalingpoints_list, use_scalingpoint=True)

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        for m in models:
            Helper._insertScalingPoint(cursor, m.zero_point, m.span_value, m.gas_concentration, m.timestamp, m.sampling_point_id, createdby)

        if not values.empty:
            set_log_context(cursor, 'scaling')
            Helper._insertScaledValues(cursor, values.to_dict("records"))

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/delete", methods=['POST'])
@jwt_required_with_processing_claim()
def delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for samplingpoint")

        # Resolve all group members at this timestamp
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
            SELECT sc.id, sc.sampling_point_id, sc.zero_point::float, sc.span_value::float, sc.gas_concentration::float
            FROM scaling_points sc
            JOIN related r ON r.id = sc.sampling_point_id
            WHERE sc.timestamp = %(timestamp)s
        """, {"sp_id": model.sampling_point_id, "timestamp": model.timestamp})
        group_sps = cursor.fetchall()

        if not group_sps:
            raise BadRequest("No scaling point found at that timestamp.")

        scalingpoints_list = [
            {"sampling_point_id": row["sampling_point_id"], "zero_point": row["zero_point"], "span_value": row["span_value"], "gas_concentration": row["gas_concentration"], "timestamp": model.timestamp}
            for row in group_sps
        ]

        values = Scaling.ReScale(cursor, scalingpoints_list, use_scalingpoint=False)

        if not values.empty and len(values[values["observationverification_id"] == 1]) > 0:
            raise Exception("Cannot scale values with verification flag 1")

        if not values.empty:
            values = Importing.process_scaled_values(cursor, values, False)

        for row in group_sps:
            deleted = Helper._deleteScalingPoint(cursor, row["id"])
            if deleted == 0:
                raise BadRequest(description=f"Could not delete scaling point {row['id']}.")

        if not values.empty:
            set_log_context(cursor, 'scaling')
            Helper._insertScaledValues(cursor, values.to_dict("records"))

        return jsonify({"success": True})


@scale_endpoint.route("/api/processing/scale/scaling_points/preview", methods=['POST'])
@jwt_required_with_processing_claim()
def preview():
    with CursorFromPool() as cursor:
        items = request.json if isinstance(request.json, list) else [request.json]
        models = [PreviewModel(**item) for item in items]

        for m in models:
            if Q.has_no_access(m.sampling_point_id):
                raise BadRequest("Access denied for samplingpoint")

        primary = models[0]
        current_timestamp = primary.current_timestamp if primary.current_timestamp is not None else primary.timestamp

        affected = Scaling.GetAffectedRange(cursor, primary.sampling_point_id, primary.timestamp, current_timestamp)
        range_min = affected["min"].isoformat() if affected["min"] else None
        range_max = affected["max"].isoformat() if affected["max"] else None

        scalingpoints_list = [
            {"sampling_point_id": m.sampling_point_id, "zero_point": m.zero_point, "span_value": m.span_value, "gas_concentration": m.gas_concentration, "timestamp": m.timestamp}
            for m in models
        ]

        values = Scaling.ReScale(cursor, scalingpoints_list, use_scalingpoint=True, old_timestamp=current_timestamp)

        if values.empty:
            return {"message": "No observations found in the affected time range", "values": [], "range": {"min": range_min, "max": range_max}}

        hasVerifiedValues = len(values[values["observationverification_id"] == 1]) > 0

        values = Importing.process_scaled_values(cursor, values, False)

        def _fmt(row):
            def _v(x):
                return None if (x is None or (isinstance(x, float) and pd.isna(x))) else x
            validity = row.get("observationvalidity_id")
            scaled = _v(row.get("scaled_value"))
            # Treat invalid (negative validity) and sentinel (-9900) as null for charting
            if validity is not None and validity < 0:
                scaled = None
            elif scaled is not None and scaled == -9900:
                scaled = None
            imp = _v(row.get("import_value"))
            if imp is not None and imp == -9900:
                imp = None
            return {
                "to_time": row["to_time"].strftime("%Y-%m-%dT%H:%M:%S") if pd.notna(row["to_time"]) else None,
                "import_value": imp,
                "scaled_value": scaled,
                "sampling_point_id": row["sampling_point_id"],
            }

        # Group results by sampling_point_id
        grouped = {}
        for _, row in values.iterrows():
            sp_id = row["sampling_point_id"]
            if sp_id not in grouped:
                grouped[sp_id] = []
            grouped[sp_id].append(_fmt(row))

        # Look up pollutant names for all SPs that appear in the result
        sp_ids_in_result = list(grouped.keys())
        cursor.execute("""
            SELECT sp.id, COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant
            FROM sampling_points sp
            JOIN eea_pollutants p ON p.id = sp.pollutant_id
            WHERE sp.id = ANY(%(sp_ids)s)
        """, {"sp_ids": sp_ids_in_result})
        pollutant_map = {row["id"]: row["pollutant"] for row in cursor.fetchall()}

        result_values = [{"sampling_point_id": sp_id, "pollutant": pollutant_map.get(sp_id, sp_id), "values": rows} for sp_id, rows in grouped.items()]

        return {"message": "The data contains verified values" if hasVerifiedValues else "", "values": result_values, "range": {"min": range_min, "max": range_max}}


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
              AND NOT EXISTS (SELECT 1 FROM calculated_series cs2 WHERE cs2.result = sp.id)
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
