"""
Filter rules for the Observation Change History.

The AirQUIS import left single sampling points carrying up to 136,192 log rows, most
of them machine traffic (ADACS imports, the migration backfill). This module turns an
administrator's filter rules into a SQL predicate so the noise never reaches the
client.

WHY IN SQL AND NOT IN THE BROWSER
---------------------------------
The history is paginated. If filtering happened after fetching, `limit` would count
rows *before* filtering: a "hide adacs_import" rule against a sampling point that is
95% ADACS would return pages of zero or one visible row, forever, and `has_more`
would be a lie. Applying the rules inside the WHERE makes `limit` count visible rows
and keeps OFFSET coherent. Plugins therefore register SQL providers (below) rather
than filtering their own columns client-side.

THE RULE SHAPE
--------------
    { "id": "r1a7f", "label": "ADACS imports", "action": "hide" | "keep",
      "enabled_by_default": true, "match": "all" | "any",
      "conditions": [ { "field": "change_source", "op": "eq", "value": "adacs_import" } ] }

Transitions need no special case: "pre-verified -> verified" is a two-condition
match:"all" rule over old_verification and new_verification. Those are genuinely two
columns, so encoding them as two conditions is the honest representation and keeps
the grammar one level deep.

COMPOSITION
-----------
    visible  iff  no enabled hide-rule matches
             AND  (there are no enabled keep-rules OR at least one matches)

Standard allow/deny. Order-independent, so adding a rule can never reorder-break an
existing one.

THE NULL INVARIANT
------------------
Negation is ALWAYS emitted as `NOT COALESCE(<base>, FALSE)`, never `<>` or `NOT IN`.
Under SQL three-valued logic `changed_by <> 'x'` is NULL — not true — when changed_by
is NULL, so a naive "hide where changed_by is not x" would also hide every system and
ADACS row, which are exactly the NULL ones. COALESCE makes negation total.

SAFETY
------
Field names are never taken from the request. A condition names a *key*; the key must
be present in the registry, and only the registry's own SQL expression is
interpolated. Values are always bound parameters.
"""
import logging

logger = logging.getLogger(__name__)


class FilterRuleError(ValueError):
    """A malformed, unknown or unsupported filter rule.

    Deliberately not werkzeug's BadRequest: this module is a pure translator with no
    web framework in it, which is what lets the whole operator table be unit-tested
    without Flask installed. The endpoint maps this to a 400.
    """

# An `in` list longer than this is a mistake or an attack, not a filter.
MAX_IN_LIST = 200

# Optimisation fence appended inside every plugin EXISTS subquery. `OFFSET 0` is a
# no-op semantically and blocks subquery pull-up, which is the entire point.
#
# Measured on raven-airquis, "comment contains Skalert" over sampling point 1511
# (136,192 log rows, 3.6M extension rows):
#
#     without the fence   5179 ms
#     with the fence       106 ms      (49x)
#
# Without it the planner rewrites the correlated EXISTS into `id = ANY(hashed
# SubPlan)`, which sequentially scans all 3.6M extension rows applying ILIKE to every
# one -- once per partition -- and ignores that the outer query is already narrowed to
# a single sampling point. With the fence it keeps the correlated form and does one
# index lookup per candidate row on the plugin's own observation_log_id index.
#
# The outer query is always bounded by sampling_point_id and LIMIT, so the correlated
# form is the right shape here essentially always. A plugin's exists_sql must
# therefore be a plain SELECT with no LIMIT or OFFSET of its own.
EXISTS_FENCE = ' OFFSET 0'

# Ops usable per field kind. A rule naming an op outside its field's kind is a 400,
# not a silently dropped condition: silently dropping a hide-rule would show rows the
# user asked to hide, which is the worse failure.
OPS_BY_KIND = {
    'text': ['eq', 'ne', 'in', 'not_in', 'contains', 'not_contains', 'empty', 'not_empty'],
    'int': ['eq', 'ne', 'in', 'not_in', 'empty', 'not_empty'],
    'numeric': ['eq', 'ne', 'between', 'empty', 'not_empty'],
    'datetime': ['between', 'empty', 'not_empty'],
}

# Each negative op is the exact negation of one positive base op. Defining them as a
# pair rather than as independent SQL is what guarantees the NULL invariant holds
# uniformly -- there is only one place that can get it wrong.
NEGATED = {
    'ne': 'eq',
    'not_in': 'in',
    'not_contains': 'contains',
    'empty': 'not_empty',
}

CORE_FILTER_FIELDS = {
    'change_source':    {'expr': 'l.change_source',    'kind': 'text'},
    'changed_by':       {'expr': 'l.changed_by',       'kind': 'text'},
    'changed_at':       {'expr': 'l.changed_at',       'kind': 'datetime'},
    'old_verification': {'expr': 'l.old_verification', 'kind': 'int'},
    'new_verification': {'expr': 'l.new_verification', 'kind': 'int'},
    'old_validity':     {'expr': 'l.old_validity',     'kind': 'int'},
    'new_validity':     {'expr': 'l.new_validity',     'kind': 'int'},
    'old_value':        {'expr': 'l.old_value',        'kind': 'numeric'},
    'new_value':        {'expr': 'l.new_value',        'kind': 'numeric'},
}

# Plugin-contributed fields, keyed '<plugin_id>.<field>'. Populated by register().
_PLUGIN_FILTER_FIELDS = {}


def register_log_filter_field(key, kind, ops, expr, exists_sql):
    """Let a plugin make one of its own columns filterable in the history.

    Called from a plugin's register(app). The plugin supplies an EXISTS template
    carrying a `{predicate}` placeholder which core fills from its own operator table,
    so no request-derived string ever becomes SQL:

        register_log_filter_field(
            key='nilu_qa.log_text', kind='text',
            ops=['contains', 'not_contains', 'empty', 'not_empty'],
            expr='_x.log_text',
            exists_sql=('SELECT 1 FROM plugin_observation_log_extended _x '
                        'WHERE _x.observation_log_id = l.id AND {predicate}'))

    EXISTS rather than a LEFT JOIN, for two reasons:

      * No row multiplication. plugin_observation_log_extended is documented 1:1 with
        observation_log but has no unique constraint enforcing it, and a join that
        matched twice would duplicate history rows and corrupt LIMIT counting.
      * Negation comes out right for free. NOT EXISTS(... AND log_text ILIKE :p)
        means "no extension row whose comment matches", which correctly INCLUDES log
        rows that have no extension row at all. A LEFT JOIN with NOT (... ILIKE ...)
        would drop those via NULL.

    Keys are namespaced so two plugins cannot collide and an orphaned rule stays
    self-describing after its plugin is removed.
    """
    if key in CORE_FILTER_FIELDS:
        raise ValueError(f'{key} collides with a core filter field')
    if '.' not in key:
        raise ValueError(f'plugin filter field {key!r} must be namespaced <plugin>.<field>')
    if '{predicate}' not in exists_sql:
        raise ValueError(f'exists_sql for {key} must contain a {{predicate}} placeholder')
    unknown = set(ops) - set(OPS_BY_KIND.get(kind, []))
    if unknown:
        raise ValueError(f'{key}: ops {sorted(unknown)} are not valid for kind {kind!r}')

    _PLUGIN_FILTER_FIELDS[key] = {
        'expr': expr, 'kind': kind, 'ops': ops, 'exists_sql': exists_sql,
    }
    logger.info('Registered observation log filter field %s', key)


def unregister_log_filter_fields(plugin_id):
    """Drop a plugin's fields, so disabling it makes its rules unavailable rather
    than silently mis-evaluated."""
    for key in [k for k in _PLUGIN_FILTER_FIELDS if k.startswith(f'{plugin_id}.')]:
        del _PLUGIN_FILTER_FIELDS[key]


def get_field(key):
    """Registry lookup; None when the field is unknown (plugin absent, or the plugin
    declares the column client-side only)."""
    if key in CORE_FILTER_FIELDS:
        f = dict(CORE_FILTER_FIELDS[key])
        f.setdefault('ops', OPS_BY_KIND[f['kind']])
        f.setdefault('exists_sql', None)
        return f
    return _PLUGIN_FILTER_FIELDS.get(key)


# ---------------------------------------------------------------------------
# Value coercion
# ---------------------------------------------------------------------------

def _coerce(value, kind, field_key):
    """Coerce a request value to the field's type, or 400.

    Rejecting here rather than letting Postgres raise keeps a bad rule from turning
    into a 500, and keeps type errors attributable to a specific field.
    """
    try:
        if kind == 'int':
            return int(value)
        if kind == 'numeric':
            return float(value)
        return str(value)
    except (TypeError, ValueError):
        raise FilterRuleError(f'filter field {field_key!r} expects a {kind} value, got {value!r}')


def _cast(kind):
    """SQL cast for a bound parameter, where the column type needs one."""
    return '::timestamp' if kind == 'datetime' else ''


# ---------------------------------------------------------------------------
# Condition -> SQL
# ---------------------------------------------------------------------------

def _base_predicate(op, expr, kind, condition, field_key, params, pname):
    """SQL for one POSITIVE operator. Negative ops are handled by the caller as the
    negation of their positive twin, so this function only ever sees eq/in/contains/
    not_empty/between."""
    if op == 'eq':
        value = condition.get('value')
        if value is None:
            return f'{expr} IS NULL'
        params[pname] = _coerce(value, kind, field_key)
        return f'{expr} = %({pname})s{_cast(kind)}'

    if op == 'in':
        values = condition.get('value')
        if not isinstance(values, list) or not values:
            raise FilterRuleError(f'filter field {field_key!r}: "in" needs a non-empty list')
        if len(values) > MAX_IN_LIST:
            raise FilterRuleError(
                f'filter field {field_key!r}: "in" list of {len(values)} exceeds the '
                f'limit of {MAX_IN_LIST}')
        params[pname] = [_coerce(v, kind, field_key) for v in values]
        return f'{expr} = ANY(%({pname})s)'

    if op == 'contains':
        params[pname] = f'%{_coerce(condition.get("value"), kind, field_key)}%'
        return f'{expr} ILIKE %({pname})s'

    if op == 'not_empty':
        # NULL and '' are both "no value". Defining not_empty as the positive form and
        # empty as its negation makes both come out right through EXISTS: "empty"
        # then correctly includes rows with no extension row at all.
        return f'({expr} IS NOT NULL AND {expr}::text <> \'\')'

    if op == 'between':
        lo, hi = condition.get('from'), condition.get('to')
        if lo is None or hi is None:
            raise FilterRuleError(f'filter field {field_key!r}: "between" needs from and to')
        params[f'{pname}_a'] = _coerce(lo, kind, field_key)
        params[f'{pname}_b'] = _coerce(hi, kind, field_key)
        c = _cast(kind)
        return f'({expr} >= %({pname}_a)s{c} AND {expr} < %({pname}_b)s{c})'

    raise FilterRuleError(f'unsupported filter operator {op!r}')


def _condition_sql(condition, params, pname):
    """SQL for one condition, total (never NULL) for negative operators."""
    if not isinstance(condition, dict):
        raise FilterRuleError('each filter condition must be an object')

    field_key = condition.get('field')
    op = condition.get('op')

    field = get_field(field_key)
    if field is None:
        # Never silently ignored -- see the module docstring. Callers filter unknown
        # fields out via rule scope before reaching here, so this is a real error.
        raise FilterRuleError(f'unknown filter field {field_key!r}')
    if op not in field['ops']:
        raise FilterRuleError(
            f'operator {op!r} is not valid for filter field {field_key!r} '
            f'(allowed: {", ".join(field["ops"])})')

    negate = op in NEGATED
    base_op = NEGATED.get(op, op)
    base = _base_predicate(base_op, field['expr'], field['kind'],
                           condition, field_key, params, pname)

    if field.get('exists_sql'):
        wrapped = 'EXISTS (' + field['exists_sql'].format(predicate=base) + EXISTS_FENCE + ')'
        # EXISTS is already total, so plain NOT is correct and COALESCE is redundant.
        return f'NOT {wrapped}' if negate else wrapped

    return f'NOT COALESCE({base}, FALSE)' if negate else base


def _rule_sql(rule, params, prefix):
    """SQL for one rule: its conditions joined by match. Not yet total -- the caller
    wraps it, because hide and keep wrap differently."""
    conditions = rule.get('conditions') or []
    if not conditions:
        raise FilterRuleError(f'filter rule {rule.get("id")!r} has no conditions')

    joiner = ' OR ' if rule.get('match') == 'any' else ' AND '
    parts = [_condition_sql(c, params, f'{prefix}_{i}') for i, c in enumerate(conditions)]
    return '(' + joiner.join(parts) + ')'


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def resolve_rules(config, overrides=None, session_disabled=()):
    """Annotate the stored rules with `enabled` and `scope`.

    Three layers, in increasing precedence:

      1. the rule's own `enabled_by_default`, set by whoever authored it;
      2. `overrides` -- the user's stored {rule_id: bool}, which is why it is a map
         rather than a list of disabled ids. A list could only ever turn rules off,
         so a rule shipped with enabled_by_default=false would be impossible for a
         user to switch on;
      3. `session_disabled` -- the "Show all" escape hatch, which suspends rules for
         one view without writing anything to the user's preferences.

    scope is 'server' when every field the rule names is in the registry, so the whole
    rule can be pushed into SQL. Otherwise 'client': the server cannot evaluate it and
    must not pretend to. Only the client knows whether an unregistered field belongs to
    a plugin that is loaded (evaluate it there) or to one that is gone (grey it out).
    """
    overrides = overrides or {}
    suspended = set(session_disabled or ())
    resolved = []
    for rule in (config or {}).get('rules', []):
        rule_id = rule.get('id')
        fields = [c.get('field') for c in (rule.get('conditions') or [])]
        scope = 'server' if fields and all(get_field(f) for f in fields) else 'client'
        enabled = bool(overrides.get(rule_id, rule.get('enabled_by_default', True)))
        resolved.append({
            **rule,
            'enabled': enabled and rule_id not in suspended,
            'scope': scope,
        })
    return resolved


def build_where(rules):
    """Translate the server-scoped enabled rules into `(sql_fragment, params)`.

    The fragment is a series of `AND ...` clauses ready to append to an existing
    WHERE, or '' when nothing is pushable.
    """
    params = {}
    enabled = [r for r in rules if r.get('enabled')]
    hides = [r for r in enabled if r.get('action') != 'keep' and r.get('scope') == 'server']
    keeps = [r for r in enabled if r.get('action') == 'keep']

    clauses = []

    # Hide rules are independent: each one removes rows on its own, so a client-scoped
    # hide rule elsewhere does not stop this one being pushed down.
    for i, rule in enumerate(hides):
        sql = _rule_sql(rule, params, f'h{i}')
        clauses.append(f'AND NOT COALESCE({sql}, FALSE)')

    # Keep rules compose as an OR, so they are all-or-nothing: pushing down a subset of
    # an OR would drop rows that the client-scoped member would have restored. If any
    # enabled keep rule cannot be evaluated here, none of them are.
    if keeps and all(r.get('scope') == 'server' for r in keeps):
        parts = [f'COALESCE({_rule_sql(r, params, f"k{i}")}, FALSE)'
                 for i, r in enumerate(keeps)]
        clauses.append('AND (' + ' OR '.join(parts) + ')')

    return ('\n            '.join(clauses), params)
