from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query import Q
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim

log_endpoint = Blueprint('observation_log', __name__)


@log_endpoint.route('/api/qualitycontrol/log', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def get_log():
    sampling_point_id = request.args.get('sampling_point_id')
    from_dt = request.args.get('from_dt')
    to_dt = request.args.get('to_dt')

    if not sampling_point_id:
        raise BadRequest("sampling_point_id is required")

    if Q.has_no_access(sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        params = {"sp_id": sampling_point_id}
        period_filter = ""
        if from_dt and to_dt:
            period_filter = "AND l.period && tsrange(%(from_dt)s::timestamp, %(to_dt)s::timestamp)"
            params["from_dt"] = from_dt
            params["to_dt"] = to_dt

        cursor.execute(f"""
            SELECT
                l.id,
                to_char(l.changed_at, 'YYYY-MM-DD HH24:MI:SS') AS changed_at,
                l.changed_by,
                l.change_source,
                to_char(lower(l.period), 'YYYY-MM-DD HH24:MI') AS period_from,
                to_char(upper(l.period), 'YYYY-MM-DD HH24:MI') AS period_to,
                l.old_verification,
                l.new_verification,
                l.old_validity,
                l.new_validity,
                l.old_value,
                l.new_value
            FROM observation_log l
            WHERE l.sampling_point_id = %(sp_id)s
            {period_filter}
            ORDER BY l.changed_at DESC
            LIMIT 500
        """, params)
        return jsonify(cursor.fetchall())
