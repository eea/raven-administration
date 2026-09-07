"""AQR3 CAM ComplianceAssessmentMethod CRUD.

CAM is derived, not entered: `core/reporting/aqr3/compliance.py` builds the row set
from the assessment regimes and the sampling points linked to them, and
POST /api/dataflow/compliance/recalculate rebuilds it. That is why this endpoint is
read-and-update only. There is no insert -- a hand-made row would need a key matching
a real regime and assessment method, and inventing one would report a compliance
situation that was never assessed -- and no delete, because AQR3's own way to retract
a row is the Deletion flag (CAM_18), which is editable here.

What *is* editable is the eight columns the evaluation is meant to compute but does
not yet. `core/data/plans_programs_export.py` supplies IsExceedance, DataCoverage,
PollutionLevel, PollutionLevelAdjusted, RelativeUncertaintyLimit, AssessmentMQI,
CorrectionFlag and PreliminaryReason as TODO-marked placeholders, so they arrive as
NULL and AQR3 wants PollutionLevel on every row. persist_compliance keeps whatever is
stored here until the evaluation produces a value of its own.

Composite primary key (reporting_year, assessment_regime_id,
data_aggregation_process_id, assessment_method_id), so this does not use the generic
Manager delete -- `Q.delete`'s `where id in (...)` cannot address it -- and the key
travels separately from the values on update.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                 jwt_required_with_management_claim)

from .models import ComplianceKey, ComplianceValues

compliance_endpoint = Blueprint('complianceassessmentmethod', __name__)

BASE = '/api/management/complianceassessmentmethod'

KEY = ('reporting_year', 'assessment_regime_id', 'data_aggregation_process_id',
       'assessment_method_id')

# The columns an operator maintains. Deliberately excludes the derived ones: a
# recalculation restates those, so an edit would be silently reverted.
VALUES = ('is_exceedance', 'data_coverage', 'pollution_level', 'pollution_level_adjusted',
          'relative_uncertainty_limit', 'assessment_mqi', 'correction_flag',
          'preliminary_reason_id', 'deletion')


@compliance_endpoint.route(BASE, methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def compliance_rows():
    """One reporting year's rows, joined for display.

    A year is required rather than defaulted: the table holds every year that has been
    calculated, and showing them mixed together would make two rows that differ only
    by year look like duplicates.
    """
    year = request.args.get('year', type=int)
    if year is None:
        raise BadRequest('A "year" query parameter is required')

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT c.reporting_year,
                   c.assessment_regime_id,
                   c.data_aggregation_process_id,
                   c.assessment_method_id,
                   c.pollutant_id,
                   COALESCE(NULLIF(p.notation, ''), p.label)   as pollutant,
                   c.assessment_type_id,
                   COALESCE(NULLIF(t.notation, ''), t.label)   as assessment_type,
                   COALESCE(NULLIF(ap.notation, ''), ap.label) as data_aggregation_process,
                   c.attainment_id,
                   c.srs_id,
                   c.calculated_at,
                   z.id                                        as zone_id,
                   z.name                                      as zone_name,
                   ot.notation                                 as objective_type,
                   rm.notation                                 as reporting_metric,
                   c.is_exceedance,
                   c.data_coverage,
                   c.pollution_level,
                   c.pollution_level_adjusted,
                   c.relative_uncertainty_limit,
                   c.assessment_mqi,
                   c.correction_flag,
                   c.preliminary_reason_id,
                   COALESCE(NULLIF(er.notation, ''), er.label) as preliminary_reason,
                   c.deletion
            FROM compliance_assessment_method c
            LEFT JOIN eea_pollutants p          ON p.id  = c.pollutant_id
            LEFT JOIN eea_assessmenttypes t     ON t.id  = c.assessment_type_id
            LEFT JOIN eea_aggregationprocess ap ON ap.id = c.data_aggregation_process_id
            LEFT JOIN eea_exceedancereason er   ON er.id = c.preliminary_reason_id
            LEFT JOIN assessment_regimes ar     ON ar.id = c.assessment_regime_id
            LEFT JOIN zones z                   ON z.id  = ar.zone_id
            LEFT JOIN eea_objectivetypes ot     ON ot.id = ar.objective_type_id
            LEFT JOIN eea_reportingmetrics rm   ON rm.id = ar.reporting_metric_id
            WHERE c.reporting_year = %(year)s
            ORDER BY c.assessment_regime_id, c.assessment_method_id,
                     c.data_aggregation_process_id
        """, {'year': year})
        return jsonify(cursor.fetchall())


@compliance_endpoint.route(f'{BASE}/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def compliance_lookups():
    """The one vocabulary an operator picks from, plus the calculated years.

    Years come from the table itself rather than from the Dataflow page's
    available_years: this screen can only show rows that exist, and that endpoint is
    behind the exporting claim, which a management user need not have.
    """
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT id as value, COALESCE(NULLIF(notation, ''), label) as label
            FROM eea_exceedancereason
            ORDER BY LOWER(label)
        """)
        reasons = cursor.fetchall()

        cursor.execute("""
            SELECT DISTINCT reporting_year as value
            FROM compliance_assessment_method
            ORDER BY reporting_year DESC
        """)
        years = [row['value'] for row in cursor.fetchall()]

        return jsonify({'reasons': reasons, 'years': years})


@compliance_endpoint.route(f'{BASE}/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def compliance_update():
    """Update the operator-maintained columns of one row, identified by `key`.

    The key is addressed, never rewritten: it is derived from the regime and the
    assessment method, and changing it here would describe a different compliance
    situation rather than correct this one.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest('Body must be {key: {reporting_year, assessment_regime_id, '
                         'data_aggregation_process_id, assessment_method_id}, '
                         'values: {...}}')

    key = ComplianceKey(**body['key'])
    model = ComplianceValues(**body['values'])

    assignments = ', '.join(f'{c} = %({c})s' for c in VALUES)
    params = {c: model[c] for c in VALUES}
    # `deletion` is NOT NULL with a false default, unlike the other eight, so an
    # omitted checkbox has to become false rather than NULL.
    params['deletion'] = bool(model.deletion)
    params.update({c: key[c] for c in KEY})

    with CursorFromPool() as cursor:
        cursor.execute(f"""
            UPDATE compliance_assessment_method
            SET {assignments}
            WHERE reporting_year = %(reporting_year)s
              AND assessment_regime_id = %(assessment_regime_id)s
              AND data_aggregation_process_id = %(data_aggregation_process_id)s
              AND assessment_method_id = %(assessment_method_id)s
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(
                f'No compliance row for {key.assessment_regime_id} / '
                f'{key.assessment_method_id} / {key.data_aggregation_process_id} in '
                f'{key.reporting_year}. Recalculate compliance on the Dataflow page if '
                f'the row set is out of date.')

    return jsonify({'msg': 'Compliance row updated successfully'})
