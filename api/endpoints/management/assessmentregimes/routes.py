"""AQR3 ARZ AssessmentRegimeZone CRUD.

`assessment_regimes` was populated only by sql/raven4_migrate/migrate_v3_to_v4.py,
so a country installing raven v4 fresh could not create one at all — and since
core/reporting/aqr3/compliance.py derives ComplianceAssessmentMethod from the
regimes, both ARZ and CAM exported empty.

Note this is a different table from `assessmentregime_zones`, which
endpoints/management/assessmentregimezones manages: that one is the zone x
environmental-objective threshold grid, and it covers only the classification
document and threshold exceedance.
"""
from flask import Blueprint, jsonify, request
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

        cursor.execute("""
            SELECT d.id AS value, d.id || ' - ' || COALESCE(dobj.label, '') AS label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
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
