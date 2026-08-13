"""Persist the computed compliance result so CAM can be reported.

`core/data/plans_programs_export.py` already evaluates exceedances against the
directive thresholds and produces everything AQR3 CAM needs, but it only ever
returned JSON for the raven-plan-program hand-off — nothing was stored, so the
ComplianceAssessmentMethod table had no source.

This module runs that evaluation and upserts it into
`compliance_assessment_method`, which the CAM entry in the export registry then
reads. Recalculating a year is idempotent: rows for that year are replaced.
"""
import logging

from core.data.plans_programs_export import PlansAndProgramsExport
from core.eea.id_generator import get_or_validate_country_code

logger = logging.getLogger(__name__)

# The evaluation reports isexceedance as a string; CAM_08 is a boolean.
_EXCEEDANCE_TRUE = {'yes', 'true', '1'}
_EXCEEDANCE_FALSE = {'no', 'false', '0'}

# The evaluation drives off sampling_points with a LEFT JOIN to assessmentdata, so
# a database with no assessment regimes yields one skipped row per sampling point —
# hundreds of near-identical entries returned to the Dataflow page. Report a sample
# and a total instead of the whole list.
_MAX_REPORTED_SKIPS = 20


def _as_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in _EXCEEDANCE_TRUE:
        return True
    if text in _EXCEEDANCE_FALSE:
        return False
    return None  # 'unknown' -> NULL rather than a misleading false


def persist_compliance(cursor, reporting_year, directive=None, pollutants=None, zones=None):
    """Evaluate compliance for `reporting_year` and store it for CAM export.

    Returns a summary dict. Rows whose assessment regime is incomplete are
    skipped and counted rather than written with a NULL primary key component.
    """
    country_code = get_or_validate_country_code(cursor)

    export = PlansAndProgramsExport(cursor)
    result = export.export_exceedances(
        countrycode=country_code,
        reportingyear=reporting_year,
        directive=directive or '2024/2881',
        pollutants=pollutants or [],
        zones=zones or [],
        exceedances_only=False,
    )
    evaluated = result.get('exceedances', [])

    # Replace the year wholesale: a regime that no longer produces a row must not
    # linger from a previous run.
    cursor.execute('DELETE FROM compliance_assessment_method WHERE reporting_year = %s',
                   (reporting_year,))

    written, skipped = 0, []
    for row in evaluated:
        regime_id = row.get('assessmentregimeid')
        method_id = row.get('assessmentmethodid')
        aggregation = row.get('dataaggregationprocessid')

        if not (regime_id and method_id and aggregation):
            skipped.append({
                'assessment_method_id': method_id,
                'reason': 'incomplete assessment regime (missing regime id, '
                          'assessment method id or aggregation process)',
            })
            continue

        cursor.execute("""
            INSERT INTO compliance_assessment_method (
                reporting_year, assessment_regime_id, data_aggregation_process_id,
                assessment_method_id, pollutant_id, assessment_type_id,
                is_exceedance, data_coverage, pollution_level, pollution_level_adjusted,
                relative_uncertainty_limit, assessment_mqi, correction_flag,
                attainment_id, srs_id, preliminary_reason_id, deletion
            ) VALUES (
                %(reporting_year)s, %(assessment_regime_id)s, %(data_aggregation_process_id)s,
                %(assessment_method_id)s, %(pollutant_id)s, %(assessment_type_id)s,
                %(is_exceedance)s, %(data_coverage)s, %(pollution_level)s, %(pollution_level_adjusted)s,
                %(relative_uncertainty_limit)s, %(assessment_mqi)s, %(correction_flag)s,
                %(attainment_id)s, %(srs_id)s, %(preliminary_reason_id)s, false
            )
            ON CONFLICT (reporting_year, assessment_regime_id,
                         data_aggregation_process_id, assessment_method_id)
            DO UPDATE SET
                pollutant_id               = EXCLUDED.pollutant_id,
                assessment_type_id         = EXCLUDED.assessment_type_id,
                is_exceedance              = EXCLUDED.is_exceedance,
                data_coverage              = EXCLUDED.data_coverage,
                pollution_level            = EXCLUDED.pollution_level,
                pollution_level_adjusted   = EXCLUDED.pollution_level_adjusted,
                relative_uncertainty_limit = EXCLUDED.relative_uncertainty_limit,
                assessment_mqi             = EXCLUDED.assessment_mqi,
                correction_flag            = EXCLUDED.correction_flag,
                attainment_id              = EXCLUDED.attainment_id,
                srs_id                     = EXCLUDED.srs_id,
                preliminary_reason_id      = EXCLUDED.preliminary_reason_id,
                deletion                   = false,
                calculated_at              = CURRENT_TIMESTAMP
        """, {
            'reporting_year': reporting_year,
            'assessment_regime_id': regime_id,
            'data_aggregation_process_id': aggregation,
            'assessment_method_id': method_id,
            'pollutant_id': row.get('pollutantid'),
            'assessment_type_id': row.get('assessmenttype'),
            'is_exceedance': _as_bool(row.get('isexceedance')),
            'data_coverage': row.get('datacoverage'),
            'pollution_level': row.get('airpollutionlevel'),
            'pollution_level_adjusted': row.get('airpollutionleveladjusted'),
            'relative_uncertainty_limit': row.get('relativeuncertaintylimit'),
            'assessment_mqi': row.get('assessmentmqi'),
            'correction_flag': _as_bool(row.get('correctionfactor')),
            'attainment_id': row.get('attainmentid'),
            'srs_id': row.get('srsid'),
            'preliminary_reason_id': row.get('preliminaryreason'),
        })
        written += 1

    if skipped:
        logger.warning('CAM %s: skipped %s row(s) with an incomplete assessment regime',
                       reporting_year, len(skipped))

    summary = {
        'reporting_year': reporting_year,
        'evaluated': len(evaluated),
        'written': written,
        'skipped_total': len(skipped),
        'skipped': skipped[:_MAX_REPORTED_SKIPS],
    }

    # Nothing written with everything skipped is not a partial result — it means no
    # assessment regime covers these sampling points. Say so, rather than leaving a
    # zero that reads like a successful run.
    if evaluated and not written:
        summary['message'] = (
            f'No compliance rows written for {reporting_year}: none of the '
            f'{len(evaluated)} evaluated sampling point(s) is linked to an assessment '
            f'regime. Define assessment regimes and link sampling points to them via '
            f'assessmentdata before reporting CAM.')

    return summary
