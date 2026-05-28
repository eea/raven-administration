from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from flask_jwt_extended import jwt_required
from core.database import CursorFromPool
from core.query import Q
from core.groups import Groups
from endpoints.qualitycontrol.validate.models import TimevalueModel, FlagModel
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim
from core.log_context import set_log_context

validate_endpoint = Blueprint('validate', __name__)


@validate_endpoint.route('/api/qualitycontrol/validate/timevalues', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def timevalues():
    m = TimevalueModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
              o.id,
              to_char (o.from_time, 'YYYY-MM-DD HH24:MI:SS') as "fromtime",
              to_char (o.to_time, 'YYYY-MM-DD HH24:MI:SS') as "totime",
              o.sampling_point_id as "sampling_point_id",
              o.observationvalidity_id,
              o.observationverification_id,
              o.value::double PRECISION ,
              case when o.observationvalidity_id not in (1,2,3) then null else o.value::double PRECISION end as "valid_value_only",
              o.import_value::double PRECISION
            FROM observations o
            WHERE 1=1
            AND o.from_time >= %(from_dt)s
            AND o.from_time < %(to_dt)s
            AND  o.sampling_point_id = %(sampling_point_id)s
            order by from_time
        """, m)
        rows = [dict(r) for r in cursor.fetchall()]

        # Fetch group members (other SPs in the same group)
        cursor.execute("""
            SELECT
                g2.sampling_point_id,
                COALESCE(NULLIF(p.notation, ''), p.label) AS label
            FROM sampling_point_groups g1
            JOIN sampling_point_groups g2 ON g1.group_id = g2.group_id
            JOIN sampling_points sp ON sp.id = g2.sampling_point_id
            JOIN eea_pollutants p ON p.id = sp.pollutant_id
            WHERE g1.sampling_point_id = %(sp_id)s
              AND g2.sampling_point_id != %(sp_id)s
            ORDER BY LOWER(p.notation)
        """, {"sp_id": m.sampling_point_id})
        members = [dict(r) for r in cursor.fetchall()]

        # Merge each member's values into the main rows (keyed by fromtime)
        for member in members:
            sp_id = member["sampling_point_id"]
            cursor.execute("""
                SELECT
                    to_char(o.from_time, 'YYYY-MM-DD HH24:MI:SS') AS fromtime,
                    o.value::double precision AS value,
                    o.observationvalidity_id
                FROM observations o
                WHERE o.sampling_point_id = %(sp_id)s
                  AND o.from_time >= %(from_dt)s
                  AND o.from_time < %(to_dt)s
                ORDER BY from_time
            """, {"sp_id": sp_id, "from_dt": m.from_dt, "to_dt": m.to_dt})
            member_map = {r["fromtime"]: dict(r) for r in cursor.fetchall()}
            for row in rows:
                mr = member_map.get(row["fromtime"], {})
                row[f"m_{sp_id}_value"] = mr.get("value")
                row[f"m_{sp_id}_validity"] = mr.get("observationvalidity_id")

        return jsonify({"rows": rows, "members": members})


@validate_endpoint.route('/api/qualitycontrol/validate/flag', methods=['POST'])
@jwt_required_with_qualitycontrol_claim()
def flag():
    m = FlagModel(**request.json)

    if Q.has_no_access(m.sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        set_log_context(cursor, 'qc_validate')
        cursor.execute("""
            update observations
            set observationvalidity_id = %(flag)s
            where id in %(ids_tuple)s
        """, m)
        if cursor.rowcount == 0:
            raise BadRequest("Could set validation flag")

        # Propagate flag to group members for the same time periods
        cursor.execute("SELECT DISTINCT from_time FROM observations WHERE id IN %(ids_tuple)s", m)
        from_times = tuple(row["from_time"] for row in cursor.fetchall())
        if from_times:
            member_ids = Groups.get_members(cursor, m.sampling_point_id)
            for member_id in member_ids:
                cursor.execute("""
                    UPDATE observations SET observationvalidity_id = %(flag)s
                    WHERE sampling_point_id = %(sp_id)s AND from_time IN %(from_times)s
                """, {"flag": m.flag, "sp_id": member_id, "from_times": from_times})

        return jsonify({"success": True})


## LOOKUPS ##

@validate_endpoint.route('/api/qualitycontrol/validate/timeseries', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def timeseries():
    timeseries = timeseries = Q.timeseries_with_time_by_access()
    return jsonify(timeseries)

