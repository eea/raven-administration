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
            WHERE d.datatable_id = 'assessmentregimezone'
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
        cursor.execute(f'INSERT INTO assessment_regimes ({columns}) VALUES ({values})', model)

    return jsonify({'msg': 'Assessment regime created successfully', 'id': model.id})


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_update():
    model = _validated(AssessmentRegimeModel(**request.json))
    assignments = ', '.join(f'{c} = %({c})s' for c in COLUMNS)
    with CursorFromPool() as cursor:
        cursor.execute(f"""
            UPDATE assessment_regimes SET {assignments} WHERE id = %(id)s
        """, model)
        if cursor.rowcount == 0:
            raise BadRequest('Could not update assessment regime ' + model.id)
    return jsonify({'msg': 'Assessment regime updated successfully'})


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
               rm.notation                             AS reporting_metric
        FROM zones z
        CROSS JOIN eea_environmentalobjective eo
        LEFT JOIN eea_pollutants p         ON p.id  = eo.related_pollutant
        LEFT JOIN eea_protectiontargets pt ON pt.uri = eo.protection_target
        LEFT JOIN eea_reportingmetrics rm  ON rm.uri = eo.reporting_metric
        LEFT JOIN eea_objectivetypes ot    ON eo.objective_type IN (ot.id, ot.uri, ot.notation)
        -- Only the objectives that carry a threshold, as the retired grid filtered them.
        WHERE (eo.assessment_threshold LIKE '%%UAT%%'
            OR eo.assessment_threshold LIKE '%%LAT%%'
            OR eo.assessment_threshold LIKE '%%LTO%%')
          -- ARZ_09 PollutantId is NOT NULL on assessment_regimes and is part of ARZ_02,
          -- so an objective with no related pollutant cannot become a regime at all.
          -- Excluded here rather than offered and then skipped.
          AND eo.related_pollutant IS NOT NULL
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
        -- byte-identical -- and the second would silently be reported as skipped.
        -- eo.id last makes the surviving representative deterministic.
        ORDER BY z.id, eo.related_pollutant, ot.id, pt.id, rm.id, eo.id
    ) c
    ORDER BY c.zone_national_code, c.pollutant, c.objective_type
"""


@assessmentregimes_endpoint.route('/api/management/assessmentregimes/candidates',
                                  methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_candidates():
    """Zone x environmental-objective combinations with no regime yet for a year."""
    year = request.args.get('year', type=int)
    if year is None:
        raise BadRequest('A "year" query parameter is required')

    with CursorFromPool() as cursor:
        cursor.execute(_CANDIDATE_SQL, {'year': year})
        return jsonify(cursor.fetchall())


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

    # The two optional annotations the retired grid existed to set.
    threshold = body.get('assessment_threshold_exceedance_id') or None
    document = body.get('classification_document_id') or None

    keys = {(str(c.get('zone_id')), c.get('environmental_objective_id')) for c in wanted}

    created, skipped = [], 0
    with CursorFromPool() as cursor:
        cursor.execute(_CANDIDATE_SQL, {'year': year})
        candidates = [row for row in cursor.fetchall()
                      if (str(row['zone_id']), row['environmental_objective_id']) in keys]

        for row in candidates:
            try:
                model = AssessmentRegimeModel(
                    id=None,
                    zone_id=row['zone_id'],
                    pollutant_id=row['pollutant_id'],
                    protection_target_id=row['protection_target_id'],
                    objective_type_id=row['objective_type_id'],
                    reporting_metric_id=row['reporting_metric_id'],
                    assessment_threshold_exceedance_id=threshold,
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
