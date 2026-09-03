"""
Plugin-contributed fallbacks for sampling point metadata.

WHY THIS EXISTS
---------------
Core reads a series' component, unit and time resolution from the EEA vocabulary
tables. Where no vocabulary term exists the core column is NULL by design -- migration
012 made pollutant_id / unit_id / time_resolution_id nullable precisely so that
non-reportable series stop having vocabulary rows invented for them. On raven-airquis
that is 56% of sampling points for the unit alone (every wind speed, temperature,
pressure and precipitation series), and the real values live in plugin tables.

A page that shows only the EEA columns therefore shows blanks: no component name in a
picker, no unit for a chart axis to group by, no timestep to compute coverage from.
This registry lets the plugin that owns those tables say how to fill the blank, without
core naming a plugin table anywhere. Same shape as the plugin providers in
observation_log_filters.py: the plugin supplies static SQL from its register(app), core
composes it into its own query.

    register_series_metadata(
        'sp_extended',
        join_sql='LEFT JOIN plugin_sp_extended _spx ON _spx.sampling_point_id = {sp}.id',
        fallbacks={'unit': '_spx.unit'})

    # in a core query
    f"SELECT {expr('unit', 'con.notation')} AS unit FROM ... {joins('spo')}"
    -> SELECT COALESCE(con.notation, _spx.unit) AS unit FROM ... LEFT JOIN ...

CORE ALWAYS WINS
----------------
expr() emits the core terms first, so a series that has an EEA term keeps it and a
plugin can only ever fill a NULL. With nothing registered, a single core term is
returned verbatim and joins() is empty -- a plugin-free install runs character-for-
character the SQL it ran before this module existed.

THE 1:1 CONTRACT
----------------
A registered join must match at most one row per sampling point. Core projects these
expressions into queries that return one row per series, and a join that matched twice
would duplicate them. Enforced by the provider's schema, not here:
plugin_sp_extended.sampling_point_id is a PRIMARY KEY and plugin_pollutants.id is a
SERIAL PRIMARY KEY. Where a plugin table has no such guarantee it must not use this
registry -- see the EXISTS discussion in observation_log_filters.register_log_filter_field.

NO REQUEST DATA
---------------
Every fragment here is a literal in plugin source, interpolated into SQL at query-build
time. Nothing derived from a request may reach these functions, and validation below
rejects the tokens that would make a mistake exploitable rather than merely broken.
"""
import logging

logger = logging.getLogger(__name__)

# The metadata core knows how to fill. A closed set on purpose: a plugin registering
# 'units' or 'pollutant_name' would otherwise be silently ignored, which reads exactly
# like the plugin not being installed.
SLOTS = ('pollutant', 'unit', 'timestep', 'timestep_seconds')

# Substituted with the sampling-point alias of the calling query. Required, because the
# alias differs per call site -- 'sp' in the dashboard route, 'spo' in Mean.GetTimeseries.
SP_PLACEHOLDER = '{sp}'

# Ordered, so the composed SQL is deterministic. Registration order is plugin load
# order, which core/plugins.py fixes with sorted(os.listdir(...)).
_PROVIDERS = []


def register_series_metadata(plugin_id, join_sql, fallbacks):
    """Let a plugin fill core's blank series metadata from its own tables.

    Called from a plugin's register(app).

      plugin_id  namespace, for diagnostics and to reject a double registration
      join_sql   one or more LEFT JOIN clauses, using {sp} for the sampling point alias
      fallbacks  {slot: sql_expression}, slot from SLOTS, expression referencing the
                 aliases introduced by join_sql

    Alias plugin tables with a leading underscore (_spx, _spp). Core's own queries use
    short unprefixed aliases -- sp, s, po, t, u, lp in the dashboard route and spo, sta,
    po, ti, con, net, lp in Mean.GetTimeseries -- and a collision would either fail to
    parse or, worse, silently resolve against the wrong table.

    Raises ValueError on anything malformed. core/plugins.py catches a failing
    register() and logs it, so a bad fragment costs that plugin its load rather than the
    whole app; raising is still right, because the alternative is a plugin that appears
    installed while contributing nothing.
    """
    if not plugin_id:
        raise ValueError('plugin_id is required')
    if any(p['plugin_id'] == plugin_id for p in _PROVIDERS):
        raise ValueError(f'{plugin_id} has already registered series metadata')
    if SP_PLACEHOLDER not in join_sql:
        raise ValueError(f'{plugin_id}: join_sql must contain a {SP_PLACEHOLDER} placeholder '
                         'for the sampling point alias')

    unknown = set(fallbacks) - set(SLOTS)
    if unknown:
        raise ValueError(f'{plugin_id}: unknown metadata slot(s) {sorted(unknown)}; '
                         f'expected any of {list(SLOTS)}')
    if not fallbacks:
        raise ValueError(f'{plugin_id}: at least one fallback expression is required')

    for fragment in (join_sql, *fallbacks.values()):
        if not isinstance(fragment, str) or not fragment.strip():
            raise ValueError(f'{plugin_id}: SQL fragments must be non-empty strings')
        # A statement terminator or line comment in a fragment can only be a mistake,
        # and is the mistake that turns a broken query into an injectable one.
        if ';' in fragment or '--' in fragment:
            raise ValueError(f'{plugin_id}: SQL fragments may not contain ";" or "--"')
        # Core executes these queries with bound parameters, and psycopg2 %-formats the
        # whole statement when it does -- so a literal % is read as a placeholder and the
        # query dies with "dict is not a sequence", nowhere near the plugin that caused
        # it. Rejected rather than escaped here, because whether %% survives depends on
        # whether the eventual call site happens to pass parameters.
        if '%' in fragment:
            raise ValueError(f'{plugin_id}: SQL fragments may not contain "%"; core '
                             'executes with bound parameters, so use mod(x, y) instead '
                             "of x % y and chr(37) for a literal percent sign")

    # LEFT, always. An inner join here would drop every sampling point that has no
    # plugin row -- i.e. it would hide most of the database from a core query that has
    # nothing to do with this plugin.
    joined = ' ' + ' '.join(join_sql.split()).upper() + ' '
    if not joined.lstrip().startswith('LEFT JOIN'):
        raise ValueError(f'{plugin_id}: join_sql must start with LEFT JOIN')
    if joined.count(' JOIN ') != joined.count(' LEFT JOIN '):
        raise ValueError(f'{plugin_id}: every clause in join_sql must be a LEFT JOIN')

    _PROVIDERS.append({
        'plugin_id': plugin_id,
        'join_sql': join_sql,
        'fallbacks': dict(fallbacks),
    })
    logger.info('Registered series metadata provider %s for %s',
                plugin_id, sorted(fallbacks))


def unregister_series_metadata(plugin_id):
    """Drop a plugin's provider. Core never calls this -- plugins are registered once at
    startup and a disable requires a restart -- but it keeps the registry testable
    without leaking state between tests."""
    _PROVIDERS[:] = [p for p in _PROVIDERS if p['plugin_id'] != plugin_id]


def providers():
    """Registered providers, in composition order. For diagnostics and tests."""
    return [dict(p) for p in _PROVIDERS]


def joins(sp_alias):
    """The LEFT JOIN clauses to append to a core query, bound to its sampling point
    alias. Empty string when no plugin has registered, so the caller needs no
    conditional."""
    if not _PROVIDERS:
        return ''
    return ' '.join(p['join_sql'].replace(SP_PLACEHOLDER, sp_alias) for p in _PROVIDERS)


def expr(slot, *core_terms):
    """Compose one metadata expression: core terms first, plugin fallbacks after.

        expr('pollutant', "NULLIF(po.notation, '')", 'po.label')
        -> COALESCE(NULLIF(po.notation, ''), po.label, _spp.notation)

    A single core term with no provider is returned as-is rather than wrapped in a
    one-argument COALESCE, so nothing changes for an install without the plugin.
    """
    if slot not in SLOTS:
        raise ValueError(f'unknown metadata slot {slot!r}; expected any of {list(SLOTS)}')
    if not core_terms:
        raise ValueError(f'{slot}: at least one core term is required')

    terms = [*core_terms]
    terms += [p['fallbacks'][slot] for p in _PROVIDERS if slot in p['fallbacks']]
    if len(terms) == 1:
        return terms[0]
    return 'COALESCE(' + ', '.join(terms) + ')'
