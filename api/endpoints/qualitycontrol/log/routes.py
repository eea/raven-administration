import json

from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query import Q
from core.jwt_ext_custom import jwt_required_with_qualitycontrol_claim
from core.observation_log_filters import FilterRuleError, build_where, resolve_rules

log_endpoint = Blueprint('observation_log', __name__)


def _load_filters(cursor, username, session_disabled):
    """Instance filter rules, resolved against this user's stored deviations.

    Returns (rules, hidden_columns). session_disabled comes from the request and is
    NOT persisted: it backs the "Show all" button, which suspends every rule for one
    view without changing what the user sees next time.
    """
    cursor.execute("SELECT observation_log_config FROM settings LIMIT 1")
    row = cursor.fetchone()
    config = (row['observation_log_config'] if row else None) or {}

    cursor.execute("""
        SELECT p.config
        FROM user_log_preferences p
        JOIN users u ON u.id = p.user_id
        WHERE u.username = %(username)s
    """, {"username": username})
    pref_row = cursor.fetchone()
    prefs = (pref_row['config'] if pref_row else None) or {}

    # A map, not a list: the user must be able to switch a rule ON as well as off,
    # which a list of disabled ids cannot express for a rule authored with
    # enabled_by_default = false.
    overrides = prefs.get('rule_overrides') or {}

    # Hidden columns are a pure display concern, so the user's list simply replaces
    # the instance default when they have one -- unlike rules, where the user records
    # only a deviation.
    hidden = prefs.get('hidden_columns')
    if hidden is None:
        hidden = config.get('hidden_columns') or []

    return resolve_rules(config, overrides, session_disabled), hidden


@log_endpoint.route('/api/qualitycontrol/log', methods=['GET'])
@jwt_required_with_qualitycontrol_claim()
def get_log():
    sampling_point_id = request.args.get('sampling_point_id')
    from_dt = request.args.get('from_dt')
    to_dt = request.args.get('to_dt')
    limit = int(request.args.get('limit', 500))
    offset = int(request.args.get('offset', 0))
    # Session-only rule suspensions. Persisted toggles come from the user's row.
    disabled_rules = [r for r in (request.args.get('disabled_rules') or '').split(',') if r]

    if not sampling_point_id:
        raise BadRequest("sampling_point_id is required")

    if Q.has_no_access(sampling_point_id):
        raise BadRequest("Access denied for samplingpoint")

    with CursorFromPool() as cursor:
        params = {"sp_id": sampling_point_id, "limit": limit + 1, "offset": offset}
        period_filter = ""
        if from_dt and to_dt:
            period_filter = "AND l.period && tsrange(%(from_dt)s::timestamp, %(to_dt)s::timestamp)"
            params["from_dt"] = from_dt
            params["to_dt"] = to_dt

        # Filtering happens here rather than in the browser so that `limit` counts
        # VISIBLE rows. Post-filtering a page would make a "hide adacs_import" rule
        # return pages of zero rows on an ADACS-dominated sampling point, and would
        # make has_more untrue.
        rules, hidden_columns = _load_filters(cursor, get_jwt_identity(), disabled_rules)
        try:
            rule_filter, rule_params = build_where(rules)
        except FilterRuleError as e:
            # A stored rule is malformed or names a field this build does not know.
            # Surfaced rather than skipped: a dropped hide-rule would quietly show
            # rows an administrator meant to hide.
            raise BadRequest(f'Invalid observation log filter rule: {e}')
        params.update(rule_params)

        cursor.execute(f"""
            SELECT
                l.id,
                -- Read by ObservationLog.vue to scope the plugin log extension. Without
                -- it that component bails before fetching, so plugin columns (QA flag,
                -- comment) never render on the Verify page at all.
                l.sampling_point_id,
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
            {rule_filter}
            -- id DESC is a tiebreaker, not decoration. changed_at defaults to the
            -- transaction timestamp and trg_observation_log_fn writes one row per
            -- sampling point per statement, so bulk work produces large ties: on
            -- sampling point 1511, 133,991 of 136,192 rows share a changed_at with
            -- another row and the largest tie group is 1,689. LIMIT/OFFSET over a
            -- non-total order lets Postgres repeat and skip rows between pages,
            -- which the popup's small page size hits constantly.
            ORDER BY l.changed_at DESC, l.id DESC
            LIMIT %(limit)s OFFSET %(offset)s
        """, params)
        rows = [dict(r) for r in cursor.fetchall()]
        has_more = len(rows) > limit
        # The rule list rides along with the rows because the client needs it to
        # render the filter menu, and GET /api/misc/settings -- where the rules are
        # stored -- requires management AND allnetworks, which a QC operator has
        # neither of. Returning it here avoids a route that would 403 for exactly the
        # people who need it.
        return jsonify({
            "rows": rows[:limit],
            "has_more": has_more,
            "filters": {"hidden_columns": hidden_columns, "rules": rules},
        })


# ---------------------------------------------------------------------------
# Per-user history preferences
#
# Plain jwt_required, and scoped by the JWT username joined through users, exactly
# as data/favorites/routes.py does: a user's own view preferences are not a
# privileged resource, and the row filter must never come from the request body.
#
# The stored config holds only the user's DEVIATION from the instance defaults in
# settings.observation_log_config -- { disabled_rule_ids: [...], hidden_columns: [...] }
# -- never a copy of them. That is what lets an administrator change the house rules
# and have every user pick the change up instead of being shadowed by a stale snapshot.
# ---------------------------------------------------------------------------

@log_endpoint.route('/api/qualitycontrol/log/preferences', methods=['GET'])
@jwt_required()
def get_log_preferences():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT p.config
            FROM user_log_preferences p
            JOIN users u ON u.id = p.user_id
            WHERE u.username = %(username)s
        """, {"username": get_jwt_identity()})
        row = cursor.fetchone()
        return jsonify(row['config'] if row else {})


@log_endpoint.route('/api/qualitycontrol/log/preferences', methods=['POST'])
@jwt_required()
def save_log_preferences():
    config = (request.get_json(force=True) or {}).get('config')
    if not isinstance(config, dict):
        raise BadRequest('config must be an object')

    with CursorFromPool() as cursor:
        cursor.execute("""
            INSERT INTO user_log_preferences (user_id, config, updated)
            VALUES ((SELECT id FROM users WHERE username = %(username)s),
                    %(config)s, now())
            ON CONFLICT (user_id) DO UPDATE
                SET config = EXCLUDED.config, updated = now()
        """, {"username": get_jwt_identity(), "config": json.dumps(config)})
    return jsonify({"msg": "Preferences saved"})
