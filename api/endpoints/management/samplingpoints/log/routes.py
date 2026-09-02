from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q
from flask_jwt_extended import get_jwt_identity

samplingpoints_log_endpoint = Blueprint('samplingpoints_log', __name__)

VALID_TYPES = ('manual', 'daily_check', 'migration')


@samplingpoints_log_endpoint.route('/api/management/samplingpoints/log/daily_check_state', methods=['GET'])
@jwt_required_with_management_claim()
def daily_check_state():
    ids_param = request.args.get('ids', '')
    ids = [i.strip() for i in ids_param.split(',') if i.strip()]

    if not ids:
        return jsonify([])

    # Only report on sampling points the caller's networks grant access to.
    ids = list(Q.sampling_point_ids_by_networks_access(ids))
    if not ids:
        return jsonify([])

    with CursorFromPool() as cursor:
        # LEFT JOIN rather than EXISTS: the dashboard's comment dialog prefills today's
        # comment when editing it. This cannot fan out — uq_spl_daily_check_per_day is a
        # unique partial index on (sampling_point_id, created_date) where
        # type = 'daily_check', so at most one row matches per sampling point.
        cursor.execute("""
            SELECT
                sp.id AS sampling_point_id,
                (l.id IS NOT NULL) AS done_today,
                l.comment,
                l.created_by,
                to_char(l.created_at, 'YYYY-MM-DD HH24:MI') AS created_at
            FROM sampling_points sp
            LEFT JOIN sampling_point_log l
                   ON l.sampling_point_id = sp.id
                  AND l.type = 'daily_check'
                  AND l.created_date = CURRENT_DATE
            WHERE sp.id = ANY(%(ids)s)
        """, {"ids": ids})
        return jsonify(cursor.fetchall())



@samplingpoints_log_endpoint.route('/api/management/samplingpoints/log', methods=['GET'])
@jwt_required_with_management_claim()
def get_sampling_point_log():
    sampling_point_id = request.args.get('sampling_point_id')
    type_filter = request.args.get('type')
    limit = min(int(request.args.get('limit', 200)), 1000)

    if not sampling_point_id:
        raise BadRequest("sampling_point_id is required")

    if Q.has_no_access(sampling_point_id):
        raise BadRequest("Access denied for sampling point")

    with CursorFromPool() as cursor:
        params = {"sp_id": sampling_point_id, "limit": limit}
        type_clause = ""
        if type_filter:
            if type_filter not in VALID_TYPES:
                raise BadRequest(f"type must be one of: {', '.join(VALID_TYPES)}")
            type_clause = "AND l.type = %(type)s"
            params["type"] = type_filter

        cursor.execute(f"""
            SELECT
                l.id,
                to_char(l.created_at, 'YYYY-MM-DD HH24:MI:SS') AS created_at,
                l.created_by,
                l.type,
                l.comment,
                to_char(l.period_from, 'YYYY-MM-DD HH24:MI') AS period_from,
                to_char(l.period_to,   'YYYY-MM-DD HH24:MI') AS period_to
            FROM sampling_point_log l
            WHERE l.sampling_point_id = %(sp_id)s
            {type_clause}
            ORDER BY l.created_at DESC
            LIMIT %(limit)s
        """, params)
        return jsonify(cursor.fetchall())


@samplingpoints_log_endpoint.route('/api/management/samplingpoints/log/insert', methods=['POST'])
@jwt_required_with_management_claim()
def insert_sampling_point_log():
    data = request.get_json()
    if not data:
        raise BadRequest("Request body is required")

    sampling_point_id = data.get('sampling_point_id')
    entry_type = data.get('type', 'manual')
    comment = data.get('comment', '').strip()
    period_from = data.get('period_from')
    period_to = data.get('period_to')
    # Opt-in: replace today's daily-check comment instead of leaving it alone. Only the
    # dashboard's comment dialog sets it, because that is an explicit edit by the user.
    overwrite = bool(data.get('overwrite'))

    if not sampling_point_id:
        raise BadRequest("sampling_point_id is required")
    if not comment:
        raise BadRequest("comment is required")
    if not period_from:
        raise BadRequest("period_from is required")
    if not period_to:
        raise BadRequest("period_to is required")
    if entry_type not in VALID_TYPES:
        raise BadRequest(f"type must be one of: {', '.join(VALID_TYPES)}")

    if Q.has_no_access(sampling_point_id):
        raise BadRequest("Access denied for sampling point")

    created_by = get_jwt_identity()

    # Only daily checks are one-per-day. uq_spl_daily_check_per_day is a partial
    # index over type = 'daily_check', so other types can never conflict — but
    # inferring it for them would imply they can.
    conflict_clause = ""
    if entry_type == 'daily_check':
        if overwrite:
            # Only the comment is replaced: created_by / created_at still record who
            # performed the check and when, and period_from / period_to keep the window
            # it was performed for. Editing the note is not redoing the check.
            conflict_clause = ("ON CONFLICT (sampling_point_id, created_date) "
                               "WHERE type = 'daily_check' "
                               "DO UPDATE SET comment = EXCLUDED.comment")
        else:
            conflict_clause = ("ON CONFLICT (sampling_point_id, created_date) "
                               "WHERE type = 'daily_check' DO NOTHING")

    with CursorFromPool() as cursor:
        cursor.execute(f"""
            INSERT INTO sampling_point_log
                (sampling_point_id, type, comment, created_by, period_from, period_to)
            VALUES
                (%(sampling_point_id)s, %(type)s, %(comment)s, %(created_by)s,
                 %(period_from)s::timestamp, %(period_to)s::timestamp)
            {conflict_clause}
            RETURNING id
        """, {
            "sampling_point_id": sampling_point_id,
            "type": entry_type,
            "comment": comment,
            "created_by": created_by,
            "period_from": period_from,
            "period_to": period_to,
        })
        row = cursor.fetchone()
        if row is None:
            return jsonify({"already_done": True}), 200
        return jsonify({"id": row["id"]}), 201
