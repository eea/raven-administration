"""AQR3 ARZ AssessmentRegimeZone CRUD.

`assessment_regimes` was populated only by sql/raven4_migrate/migrate_v3_to_v4.py,
so a country installing raven v4 fresh could not create one at all — and since
core/reporting/aqr3/compliance.py derives ComplianceAssessmentMethod from the
regimes, both ARZ and CAM exported empty.

This is the table the ARZ export reads (core/reporting/aqr3/spec.py). A second table,
`assessmentregime_zones`, used to shadow it behind a menu entry of its own: a
zone x environmental-objective grid carrying only the classification document and the
threshold exceedance. It could not express ARZ — no AssessmentRegimeId, and pollutant,
protection target, objective type and reporting metric collapsed into a single
environmental objective — and nothing exported it, so migration 020 dropped it. Its one
useful trick, filling the zone x objective grid for a year, survives here as
/candidates and /generate, which write real regimes with derived ARZ_02 ids.
"""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.eea import assessment_threshold as at
from core.eea.id_generator import EEAIDGenerator, IdentifierError, validate_identifier
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                jwt_required_with_management_claim)
from core.query import DeleteModel, Q

from .models import AssessmentRegimeModel

assessmentregimes_endpoint = Blueprint('assessmentregimes', __name__)

# Written by both insert and update, in one place so they cannot drift.
COLUMNS = (
    'zone_id', 'pollutant_id', 'protection_target_id', 'objective_type_id',
    'reporting_metric_id', 'assessment_threshold_exceedance_id', 'postponement_year',
    'fixed_measurement_reduction', 'zone_resident_population_year',
    'zone_resident_population', 'classification_year', 'classification_document_id',
)


def _validated(model):
    """ARZ_02 has a mandatory format, so a free-text id is rejected here.

    A malformed AssessmentRegimeId is not caught until Reportnet3 validates the
    submission, by which point CAM already references it.
    """
    if not model.id:
        raise BadRequest('id is required')
    try:
        validate_identifier('AssessmentRegimeId', model.id)
    except IdentifierError as e:
        raise BadRequest(str(e))
    return model


# The environmental objectives a regime decomposes from. Several can match (the UAT/LAT
# objective and the LTO one share pollutant, objective type, target and metric), so the
# allowed classifications are their union.
_OBJECTIVES_OF_REGIME = """
    SELECT eo.assessment_threshold
      FROM eea_environmentalobjective eo
      LEFT JOIN eea_protectiontargets pt ON pt.uri = eo.protection_target
      LEFT JOIN eea_reportingmetrics rm  ON rm.uri = eo.reporting_metric
      LEFT JOIN eea_objectivetypes ot    ON eo.objective_type IN (ot.id, ot.uri, ot.notation)
     WHERE eo.related_pollutant = %(pollutant_id)s
       AND ot.id IS NOT DISTINCT FROM %(objective_type_id)s
       AND pt.id IS NOT DISTINCT FROM %(protection_target_id)s
       AND rm.id IS NOT DISTINCT FROM %(reporting_metric_id)s
"""


def _allowed_thresholds(cursor, model):
    """The AssessmentThresholdExceedance values the regime's objective allows, or None
    when no objective matches (an empty vocabulary, or a hand-made combination)."""
    cursor.execute(_OBJECTIVES_OF_REGIME, {
        'pollutant_id': model.pollutant_id, 'objective_type_id': model.objective_type_id,
        'protection_target_id': model.protection_target_id,
        'reporting_metric_id': model.reporting_metric_id})
    rows = cursor.fetchall()
    if not rows:
        return None
    return {value for row in rows for value in at.allowed_values(row['assessment_threshold'])}


def _check_threshold(cursor, model):
    """Refuse a classification the environmental objective does not allow.

    The vocabulary lists them per objective -- aboveUAT/LAT-UAT/belowLAT for a limit
    value, aboveLTO/belowLTO for ozone's long-term objective, NA for an alert threshold
    -- and Reportnet3 rejects anything else.
    """
    value = model.assessment_threshold_exceedance_id
    if not value:
        return
    allowed = _allowed_thresholds(cursor, model)
    if allowed and value not in allowed:
        raise BadRequest(f'Assessment threshold exceedance {value} is not allowed for this '
                         f'objective; the vocabulary allows {", ".join(sorted(allowed))}.')


def _derive_id(cursor, model):
    """Build a conformant ARZ_02 from the regime's own fields.

    The identifier embeds ObjectiveType, ProtectionTarget and ReportingMetric as
    their notations rather than their ids, so those are looked up.
    """
    parts = {'zone_id': model.zone_id, 'pollutant_id': model.pollutant_id,
             'objective_type_id': model.objective_type_id,
             'protection_target_id': model.protection_target_id,
             'reporting_metric_id': model.reporting_metric_id,
             'classification_year': model.classification_year}
    missing = [k for k, v in parts.items() if v in (None, '')]
    if missing:
        raise BadRequest(
            f'Either give an Id, or fill in {", ".join(sorted(missing))} so one can be '
            f'derived. AQR3 ARZ_02 has a mandatory format and cannot be free text.')

    notations = {}
    for key, table in (('objective_type_id', 'eea_objectivetypes'),
                       ('protection_target_id', 'eea_protectiontargets'),
                       ('reporting_metric_id', 'eea_reportingmetrics')):
        cursor.execute(f'SELECT notation FROM {table} WHERE id = %s', (parts[key],))
        row = cursor.fetchone()
        if row is None:
            raise BadRequest(f'Unknown {key}: {parts[key]}')
        notations[key] = row['notation']

    try:
        return EEAIDGenerator.generate_assessment_regime_id(
            parts['zone_id'], parts['pollutant_id'], notations['objective_type_id'],
            notations['protection_target_id'], notations['reporting_metric_id'],
            parts['classification_year'])
    except (IdentifierError, ValueError) as e:
        raise BadRequest(str(e))


@assessmentregimes_endpoint.route('/api/management/assessmentregimes', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT ar.id,
                   ar.zone_id, z.name AS zone,
                   ar.pollutant_id, COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant,
                   ar.protection_target_id, pt.notation AS protection_target,
                   ar.objective_type_id, ot.notation AS objective_type,
                   ar.reporting_metric_id, rm.notation AS reporting_metric,
                   ar.assessment_threshold_exceedance_id,
                   ate.notation AS assessment_threshold_exceedance,
                   ar.postponement_year,
                   ar.fixed_measurement_reduction,
                   ar.zone_resident_population_year,
                   ar.zone_resident_population,
                   ar.classification_year,
                   ar.classification_document_id
            FROM assessment_regimes ar
            LEFT JOIN zones z                   ON ar.zone_id = z.id
            LEFT JOIN eea_pollutants p          ON ar.pollutant_id = p.id
            LEFT JOIN eea_protectiontargets pt  ON ar.protection_target_id = pt.id
            LEFT JOIN eea_objectivetypes ot     ON ar.objective_type_id = ot.id
            LEFT JOIN eea_reportingmetrics rm   ON ar.reporting_metric_id = rm.id
            LEFT JOIN eea_assessmentthresholdexceedances ate
                   ON ar.assessment_threshold_exceedance_id = ate.id
            ORDER BY ar.id
        """)
        return jsonify(cursor.fetchall())


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_lookups():
    with CursorFromPool() as cursor:
        cursor.execute('SELECT id AS value, name AS label FROM zones ORDER BY LOWER(name)')
        zones = cursor.fetchall()

        pollutants = Q.pollutants_lookup()

        simple = {
            'protection_targets': 'eea_protectiontargets',
            'objective_types': 'eea_objectivetypes',
            'reporting_metrics': 'eea_reportingmetrics',
            'threshold_exceedances': 'eea_assessmentthresholdexceedances',
        }
        result = {'zones': zones, 'pollutants': pollutants}
        for key, table in simple.items():
            cursor.execute(f"""
                SELECT id AS value, COALESCE(NULLIF(notation, ''), label) AS label
                FROM {table} ORDER BY LOWER(COALESCE(NULLIF(notation, ''), label))
            """)
            result[key] = cursor.fetchall()

        # Filtered by DOC_02 DataTable, the way the retired assessmentregimezones grid
        # did it: an unfiltered list offers documents belonging to other tables as a
        # ClassificationDocumentId, which fails Reportnet3 QC rather than the form.
        cursor.execute("""
            SELECT d.id AS value,
                   d.id || ' - ' || COALESCE(NULLIF(dobj.notation, ''), dobj.label, '') AS label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            -- eea_datatable.id is 'AssessmentRegimeZone'; comparing against the
            -- lower-case spelling matched nothing, so this dropdown was always
            -- empty and no regime could be pointed at a document at all.
            WHERE lower(d.datatable_id) = 'assessmentregimezone'
            ORDER BY d.id
        """)
        result['documents'] = cursor.fetchall()

    return jsonify(result)


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_insert():
    model = AssessmentRegimeModel(**request.json)
    columns = ', '.join(('id',) + COLUMNS)
    values = ', '.join(f'%({c})s' for c in ('id',) + COLUMNS)

    with CursorFromPool() as cursor:
        if not model.id:
            model = model.model_copy(update={'id': _derive_id(cursor, model)})
        _validated(model)
        _check_threshold(cursor, model)
        cursor.execute(f'INSERT INTO assessment_regimes ({columns}) VALUES ({values})', model)

    return jsonify({'msg': 'Assessment regime created successfully', 'id': model.id})


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_update():
    model = AssessmentRegimeModel(**request.json)
    if not model.id:
        raise BadRequest('id is required')

    with CursorFromPool() as cursor:
        # A migrated regime can carry an identifier that predates ARZ_02
        # validation. Validating it here as well as on insert froze those rows
        # solid: the row was refused whatever you were trying to change, so the
        # zone a regime needs before its identifier can be rebuilt could never be
        # filled in. The id is not editable in this form and this route does not
        # write it, so an existing row is allowed through unchanged -- which is
        # what makes it repairable. New ids are still validated on insert.
        cursor.execute('SELECT 1 FROM assessment_regimes WHERE id = %s', (model.id,))
        existing = cursor.fetchone() is not None
        if not existing:
            _validated(model)
        _check_threshold(cursor, model)

        assignments = ', '.join(f'{c} = %({c})s' for c in COLUMNS)
        cursor.execute(f"""
            UPDATE assessment_regimes SET {assignments} WHERE id = %(id)s
        """, model)
        if cursor.rowcount == 0:
            raise BadRequest('Could not update assessment regime ' + model.id)
    return jsonify({'msg': 'Assessment regime updated successfully'})


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/repair-id',
                                  methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_repair_id():
    """Rebuild a regime's AssessmentRegimeId from its own fields.

    A regime migrated from v3 can carry an identifier that predates ARZ_02
    validation. That is not a cosmetic problem: `_validated()` runs on every
    update, so the whole row is refused and the regime cannot be edited at all --
    not even to fix an unrelated field. The id itself is not editable in the UI
    either, by design, because it is derived rather than typed. Without this
    route the only way out is delete and recreate, which cascades away the
    regime's assessment data and compliance rows.

    The id is rebuilt, never patched: the mandatory format has seven segments and
    a four-digit pollutant, so no amount of string surgery on an old id produces
    a valid one. A regime missing any component is refused rather than guessed --
    choosing a zone is a decision for a person.

    `assessmentdata`, `attainments` and `compliance_assessment_method` all
    declare `on update cascade`, so their rows follow.
    """
    body = request.json or {}
    current = (body.get('id') or '').strip()
    if not current:
        raise BadRequest('id is required')

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT id, zone_id, pollutant_id, objective_type_id, protection_target_id,
                   reporting_metric_id, classification_year
              FROM assessment_regimes WHERE id = %s
        """, (current,))
        row = cursor.fetchone()
        if row is None:
            raise BadRequest(f'No assessment regime with id {current}')

        parts = ('zone_id', 'pollutant_id', 'objective_type_id', 'protection_target_id',
                 'reporting_metric_id', 'classification_year')
        missing = [c for c in parts if row[c] in (None, '')]
        if missing:
            raise BadRequest(
                'The identifier is built from the zone, pollutant, objective type, '
                'protection target, reporting metric and classification year. '
                'Fill in ' + ', '.join(m.replace('_id', '').replace('_', ' ')
                                       for m in missing) + ' first.')

        # The trailing index distinguishes regimes that agree on all six, so it has
        # to be chosen against the ids that already exist rather than assumed to be 1.
        index, new_id = 0, None
        while index < 9:
            index += 1
            candidate = EEAIDGenerator.generate_assessment_regime_id(
                *(row[c] for c in parts), index)
            cursor.execute('SELECT 1 FROM assessment_regimes WHERE id = %s', (candidate,))
            if cursor.fetchone() is None or candidate == current:
                new_id = candidate
                break
        if new_id is None:
            raise BadRequest('Could not find a free index for this identifier.')

        try:
            validate_identifier('AssessmentRegimeId', new_id)
        except IdentifierError as e:
            raise BadRequest(f'The rebuilt identifier is still not valid: {e}')

        if new_id == current:
            return jsonify({'msg': 'This identifier is already correct', 'id': current,
                            'changed': False})

        cursor.execute('UPDATE assessment_regimes SET id = %s WHERE id = %s',
                       (new_id, current))
        if cursor.rowcount == 0:
            raise BadRequest(f'Could not update assessment regime {current}')

    return jsonify({'msg': f'Identifier rebuilt as {new_id}', 'id': new_id,
                    'previous': current, 'changed': True})


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete('assessment_regimes', model)
    if rows == 0:
        raise BadRequest('Could not delete for ids ' + ','.join(model.ids))
    return jsonify({'msg': 'Assessment regime deleted successfully'})


# ---------------------------------------------------------------------------
# Bulk fill, inherited from the retired assessmentregimezones grid.
#
# That grid listed `zones CROSS JOIN eea_environmentalobjective` for a year and let an
# operator annotate combinations in bulk. The annotations went to a table nothing
# exported. The same enumeration is genuinely useful here, where the rows it produces
# are real regimes: a country declares a regime per zone per objective, and typing a
# few hundred of them one popup at a time is the reason the grid existed.
#
# An environmental objective bundles what ARZ keeps as four separate attributes, so
# each candidate is decomposed on the way in — that translation is what the old table
# never did, and why its rows could not become ARZ rows.
# ---------------------------------------------------------------------------

# eea_environmentalobjective.protection_target and .reporting_metric hold URIs, not
# ids — migration 016 step 5 says so explicitly and exempts them from the id
# normalisation. objective_type is not in that exemption and the retired grid rendered
# it verbatim, so it is matched against all three candidate columns rather than
# guessed at; a vocabulary reload that changes the convention then still resolves.
_CANDIDATE_SQL = """
    SELECT * FROM (
        SELECT DISTINCT ON (z.id, eo.related_pollutant, ot.id, pt.id, rm.id)
               z.id                                    AS zone_id,
               z.name                                  AS zone_name,
               z.zone_national_code,
               eo.id                                   AS environmental_objective_id,
               eo.related_pollutant                    AS pollutant_id,
               COALESCE(NULLIF(p.notation, ''), p.label)   AS pollutant,
               ot.id                                   AS objective_type_id,
               ot.notation                             AS objective_type,
               pt.id                                   AS protection_target_id,
               pt.notation                             AS protection_target,
               rm.id                                   AS reporting_metric_id,
               rm.notation                             AS reporting_metric,
               eo.assessment_threshold                 AS allowed_thresholds,
               -- Reporting sampling points measuring the pollutant inside the zone,
               -- located by their station's coordinates, active during the year.
               (SELECT count(*) FROM sampling_points sp
                  JOIN stations st ON st.id = sp.station_id
                 WHERE sp.pollutant_id = eo.related_pollutant
                   AND sp.report_to_eea AND st.report_to_eea
                   AND st.longitude IS NOT NULL AND st.latitude IS NOT NULL
                   AND (sp.from_time IS NULL OR sp.from_time < make_date(%(year)s + 1, 1, 1))
                   AND (sp.to_time IS NULL OR sp.to_time >= make_date(%(year)s, 1, 1))
                   AND {in_zone})                     AS n_points,
               (SELECT count(*) FROM models m
                 WHERE m.pollutant_id = eo.related_pollutant) AS n_models
        FROM zones z
        CROSS JOIN eea_environmentalobjective eo
        LEFT JOIN eea_pollutants p         ON p.id  = eo.related_pollutant
        LEFT JOIN eea_protectiontargets pt ON pt.uri = eo.protection_target
        LEFT JOIN eea_reportingmetrics rm  ON rm.uri = eo.reporting_metric
        LEFT JOIN eea_objectivetypes ot    ON eo.objective_type IN (ot.id, ot.uri, ot.notation)
        -- Every objective, not only those with an upper/lower assessment threshold as
        -- the retired grid filtered them. The 2024/2881 recast has none: it has one
        -- assessment threshold (aboveAT/belowAT), and its LTO objectives have NA. And
        -- alert and information thresholds and critical levels without a threshold
        -- are regimes too -- Malta reports ALT, INT and CL regimes with NA.
        --
        -- ARZ_09 PollutantId is NOT NULL on assessment_regimes and is part of ARZ_02,
        -- so an objective with no related pollutant cannot become a regime at all.
        -- Excluded here rather than offered and then skipped.
        WHERE eo.related_pollutant IS NOT NULL
          -- A regime already covering this combination for the year is not a candidate.
          -- Matched on the five attributes ARZ_02 is derived from rather than on the id,
          -- so a regime whose id was entered by hand still counts as covering it.
          AND NOT EXISTS (
                SELECT 1 FROM assessment_regimes ar
                 WHERE ar.zone_id             = z.id
                   AND ar.classification_year = %(year)s
                   AND ar.pollutant_id        IS NOT DISTINCT FROM eo.related_pollutant
                   AND ar.objective_type_id   IS NOT DISTINCT FROM ot.id
                   AND ar.protection_target_id IS NOT DISTINCT FROM pt.id
                   AND ar.reporting_metric_id IS NOT DISTINCT FROM rm.id)
        -- DISTINCT ON, because several environmental objectives can decompose to one
        -- regime: an objective carries an assessment threshold, and ARZ does not, so the
        -- UAT/LAT objective and the LTO objective for the same pollutant, protection
        -- target, objective type and reporting metric are the same regime. Listing both
        -- would promise more rows than generating can create -- their derived ARZ_02 is
        -- byte-identical -- and the second would silently be reported as skipped. The
        -- recast also lists most objectives twice, for attainment years 2026 and 2030,
        -- which ARZ does not carry either.
        -- eo.id last makes the surviving representative deterministic.
        ORDER BY z.id, eo.related_pollutant, ot.id, pt.id, rm.id, eo.id
    ) c
    -- scope 'measured' (the wizard's default) keeps what the zone actually assesses: a
    -- pollutant with a sampling point inside the zone, or a model for it (models carry
    -- no location). It also drops the margin-of-tolerance objectives, which applied
    -- only under a time extension and lapsed in 2015. 'all' lists every combination.
    WHERE %(scope)s = 'all'
       OR ((c.n_points > 0 OR c.n_models > 0)
           AND c.objective_type IS DISTINCT FROM 'LVMOT'
           AND c.objective_type IS DISTINCT FROM 'LVmaxMOT')
    ORDER BY c.zone_national_code, c.pollutant, c.objective_type
""".replace('{in_zone}', at.IN_ZONE)


def _with_proposals(cursor, rows, year):
    """Add each candidate's proposed AssessmentThresholdExceedance and its basis.

    From the five years before the classification year, measured inside the zone; see
    core/eea/assessment_threshold.py. A zone's statistics are read once per threshold,
    however many objectives share them.
    """
    cache = {}
    for row in rows:
        allowed = at.allowed_values(row.get('allowed_thresholds'))
        row['allowed_thresholds'] = allowed
        proposal = at.classify(cursor, row['zone_id'], row['pollutant_id'],
                               row.get('protection_target'), allowed, year, cache)
        row['proposed_threshold_exceedance'] = proposal['value']
        row['proposal_basis'] = proposal['basis']
    return rows


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/candidates',
                                  methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_candidates():
    """Zone x environmental-objective combinations with no regime yet for a year.

    ?scope=measured (default) or all; ?classify=0 skips the proposed classification.
    """
    year = request.args.get('year', type=int)
    if year is None:
        raise BadRequest('A "year" query parameter is required')
    scope = request.args.get('scope', 'measured')
    if scope not in ('measured', 'all'):
        raise BadRequest('"scope" is measured or all')

    with CursorFromPool() as cursor:
        cursor.execute(_CANDIDATE_SQL, {'year': year, 'scope': scope})
        rows = cursor.fetchall()
        if request.args.get('classify', '1') != '0':
            rows = _with_proposals(cursor, rows, year)
        return jsonify(rows)


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/generate',
                                  methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_generate():
    """Create regimes for the chosen combinations, deriving each ARZ_02.

    The candidates are re-read here rather than trusted from the request: the ids are
    what the derived AssessmentRegimeId is built from, and a client that sent a
    zone/objective pair it never saw would produce a conformant-looking identifier for
    a combination that does not exist.
    """
    body = request.json or {}
    year = body.get('year')
    wanted = body.get('combinations') or []
    if not isinstance(year, int):
        raise BadRequest('"year" is required and must be a whole year')
    if not wanted:
        raise BadRequest('Select at least one combination to generate')

    # The two optional annotations the retired grid existed to set. A classification
    # given per combination wins over the one for the whole batch, and that over the
    # proposal computed from the zone's measurements. A combination that names the key
    # with an empty value asks for none: the user cleared the proposal.
    threshold = body.get('assessment_threshold_exceedance_id') or None
    document = body.get('classification_document_id') or None

    unset = object()
    chosen = {(str(c.get('zone_id')), c.get('environmental_objective_id')):
              (c.get('assessment_threshold_exceedance_id') or None)
              if 'assessment_threshold_exceedance_id' in c else unset for c in wanted}

    def key(row):
        return str(row['zone_id']), row['environmental_objective_id']

    created, skipped, refused = [], 0, []
    with CursorFromPool() as cursor:
        # 'all': whatever the dialog listed, any existing combination may be generated.
        cursor.execute(_CANDIDATE_SQL, {'year': year, 'scope': 'all'})
        candidates = [row for row in cursor.fetchall() if key(row) in chosen]
        if all(chosen[key(row)] is not unset or threshold for row in candidates):
            for row in candidates:
                row['allowed_thresholds'] = at.allowed_values(row['allowed_thresholds'])
        else:
            candidates = _with_proposals(cursor, candidates, year)

        # Checked before anything is written, so a refusal leaves nothing half done.
        for row in candidates:
            allowed = row['allowed_thresholds']
            given = chosen[key(row)]
            value = (given if given is not unset
                     else threshold or row.get('proposed_threshold_exceedance'))
            if value and allowed and value not in allowed:
                if given is not unset:
                    refused.append(f'{row["zone_national_code"]} {row["pollutant"]} '
                                   f'{row["objective_type"]}: {value}')
                # The batch-wide value does not fit this objective: fall back to the
                # proposal rather than refuse the row.
                value = row.get('proposed_threshold_exceedance')
            row['threshold_value'] = value
        if refused:
            raise BadRequest('Not an allowed classification for the objective: '
                             + '; '.join(refused[:10]) + (' ...' if len(refused) > 10 else ''))

        for row in candidates:
            value = row['threshold_value']
            try:
                model = AssessmentRegimeModel(
                    id=None,
                    zone_id=row['zone_id'],
                    pollutant_id=row['pollutant_id'],
                    protection_target_id=row['protection_target_id'],
                    objective_type_id=row['objective_type_id'],
                    reporting_metric_id=row['reporting_metric_id'],
                    assessment_threshold_exceedance_id=value,
                    classification_year=year,
                    classification_document_id=document,
                )
                model = model.model_copy(update={'id': _derive_id(cursor, model)})
            except (BadRequest, ValidationError):
                # An objective missing a pollutant or a vocabulary term cannot yield a
                # conformant ARZ_02. Skipping keeps the rest of the batch, and the
                # count says how many were left out.
                skipped += 1
                continue

            columns = ', '.join(('id',) + COLUMNS)
            values = ', '.join(f'%({c})s' for c in ('id',) + COLUMNS)
            cursor.execute(
                f'INSERT INTO assessment_regimes ({columns}) VALUES ({values}) '
                f'ON CONFLICT (id) DO NOTHING', model)
            if cursor.rowcount:
                created.append(model.id)
            else:
                skipped += 1

    return jsonify({'msg': f'Created {len(created)} assessment regimes'
                           + (f', skipped {skipped}' if skipped else ''),
                    'created': created, 'skipped': skipped})
