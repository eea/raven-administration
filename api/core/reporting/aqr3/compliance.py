"""Persist the computed compliance result so CAM can be reported.

`core/data/plans_programs_export.py` already evaluates exceedances against the
directive thresholds and produces everything AQR3 CAM needs, but it only ever
returned JSON for the raven-plan-program hand-off — nothing was stored, so the
ComplianceAssessmentMethod table had no source.

This module runs that evaluation and upserts it into
`compliance_assessment_method`, which the CAM entry in the export registry then
reads. Recalculating a year is idempotent.

TWO TIERS OF COLUMN. The key, PollutantId, AssessmentType, AttainmentId and SRSId
are derived, and a recalculation restates them. The rest -- IsExceedance,
DataCoverage, PollutionLevel, PollutionLevelAdjusted, RelativeUncertaintyLimit,
AssessmentMQI, CorrectionFlag, PreliminaryReason -- are what the evaluation is
*meant* to compute but does not yet: `core/data/plans_programs_export.py` supplies
them as TODO-marked placeholders, so they arrive as NULL. Until that evaluation
exists they are entered by hand on Management -> Compliance Assessment Method, and
this writer must not throw those entries away.

So each of them is written as COALESCE(computed, stored): a computed value wins
whenever there is one, and the typed value survives only while there is none. The
day the evaluation is implemented, real numbers take over on their own with no
change here. Deletion (CAM_18) is left out of the update entirely -- it is AQR3's
retraction flag, never computed, and COALESCE cannot express that because the
proposed row would carry the column default rather than NULL.
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


def _drop_rows_no_longer_produced(cursor, reporting_year, planned):
    """Remove the year's rows this run does not produce, and only those.

    The year used to be deleted wholesale, on the reasoning that a regime which has
    stopped yielding a row must not linger. That is still true, but it also discarded
    every hand-entered value, which the upsert now goes to some trouble to keep -- a
    DELETE followed by an INSERT leaves nothing for COALESCE to find. So the rows about
    to be rebuilt are spared and the rest still go.
    """
    keys = tuple((regime, aggregation, method)
                 for _, regime, aggregation, method in planned)
    if not keys:
        cursor.execute('DELETE FROM compliance_assessment_method WHERE reporting_year = %s',
                       (reporting_year,))
        return

    cursor.execute("""
        DELETE FROM compliance_assessment_method
         WHERE reporting_year = %(year)s
           AND (assessment_regime_id, data_aggregation_process_id, assessment_method_id)
               NOT IN %(keys)s
    """, {'year': reporting_year, 'keys': keys})


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

    # Keyed up front, so the pre-delete below knows which rows are about to be
    # rebuilt and can leave them alone.
    written, skipped, planned = 0, [], []
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

        planned.append((row, regime_id, aggregation, method_id))

    _drop_rows_no_longer_produced(cursor, reporting_year, planned)

    for row, regime_id, aggregation, method_id in planned:
        cursor.execute("""
            INSERT INTO compliance_assessment_method (
                reporting_year, assessment_regime_id, data_aggregation_process_id,
                assessment_method_id, pollutant_id, assessment_type_id,
                is_exceedance, data_coverage, pollution_level, pollution_level_adjusted,
                relative_uncertainty_limit, assessment_mqi, correction_flag,
                attainment_id, srs_id, preliminary_reason_id
            ) VALUES (
                %(reporting_year)s, %(assessment_regime_id)s, %(data_aggregation_process_id)s,
                %(assessment_method_id)s, %(pollutant_id)s, %(assessment_type_id)s,
                %(is_exceedance)s, %(data_coverage)s, %(pollution_level)s, %(pollution_level_adjusted)s,
                %(relative_uncertainty_limit)s, %(assessment_mqi)s, %(correction_flag)s,
                %(attainment_id)s, %(srs_id)s, %(preliminary_reason_id)s
            )
            ON CONFLICT (reporting_year, assessment_regime_id,
                         data_aggregation_process_id, assessment_method_id)
            DO UPDATE SET
                -- Derived: restated on every run, so a stale value cannot persist.
                pollutant_id               = EXCLUDED.pollutant_id,
                assessment_type_id         = EXCLUDED.assessment_type_id,
                attainment_id              = EXCLUDED.attainment_id,
                srs_id                     = EXCLUDED.srs_id,
                -- Not computed yet, so entered by hand: keep what is stored until the
                -- evaluation produces something. See this module's docstring.
                is_exceedance              = COALESCE(EXCLUDED.is_exceedance,
                                                      compliance_assessment_method.is_exceedance),
                data_coverage              = COALESCE(EXCLUDED.data_coverage,
                                                      compliance_assessment_method.data_coverage),
                pollution_level            = COALESCE(EXCLUDED.pollution_level,
                                                      compliance_assessment_method.pollution_level),
                pollution_level_adjusted   = COALESCE(EXCLUDED.pollution_level_adjusted,
                                                      compliance_assessment_method.pollution_level_adjusted),
                relative_uncertainty_limit = COALESCE(EXCLUDED.relative_uncertainty_limit,
                                                      compliance_assessment_method.relative_uncertainty_limit),
                assessment_mqi             = COALESCE(EXCLUDED.assessment_mqi,
                                                      compliance_assessment_method.assessment_mqi),
                correction_flag            = COALESCE(EXCLUDED.correction_flag,
                                                      compliance_assessment_method.correction_flag),
                preliminary_reason_id      = COALESCE(EXCLUDED.preliminary_reason_id,
                                                      compliance_assessment_method.preliminary_reason_id),
                -- `deletion` is absent on purpose: it is the operator's retraction flag
                -- and nothing computes it. COALESCE would not help -- the proposed row
                -- carries the column default (false), not NULL, so it would win.
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
