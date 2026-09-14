"""Persist the computed compliance result so CAM can be reported.

`core/data/plans_programs_export.py` already evaluates exceedances against the
directive thresholds and produces everything AQR3 CAM needs, but it only ever
returned JSON for the raven-plan-program hand-off — nothing was stored, so the
ComplianceAssessmentMethod table had no source.

This module runs that evaluation and upserts it into
`compliance_assessment_method`, which the CAM entry in the export registry then
reads. Recalculating a year is idempotent.

THREE TIERS OF COLUMN.

1. DERIVED, restated on every run: the key, PollutantId, AssessmentType and
   AttainmentId. These describe the row rather than measure it, so a stale value must
   not survive. AttainmentId is derived around one number it does not own -- see 3.

2. NOT COMPUTED YET, so entered by hand and preserved: IsExceedance, DataCoverage,
   PollutionLevel, PollutionLevelAdjusted, RelativeUncertaintyLimit, AssessmentMQI,
   CorrectionFlag, PreliminaryReason and SRSId. The first eight are what the
   evaluation is *meant* to compute but does not yet -- `plans_programs_export.py`
   supplies them as TODO-marked placeholders, so they arrive as NULL. SRSId is
   different in kind: nothing can ever derive it, because SRS_02 names a spatial area
   an operator uploads and SRS_06 points from that area at the model which assessed
   it, not at this row. It used to be set to the sampling point id, which pointed all
   214 distinct SRSIds in the 2026-09-09 export at an empty SpatialRepresentativeness
   table.

   Each is written as COALESCE(computed, stored): a computed value wins whenever there
   is one, and the typed value survives only while there is none. The day the
   evaluation is implemented, real numbers take over on their own with no change here.

3. THE OPERATOR'S ALONE, absent from the statement entirely: Deletion (CAM_18) and
   AttainmentIndex. Both are NOT NULL with a default, which is precisely what COALESCE
   cannot protect -- the proposed row carries the default rather than NULL, so it would
   win every time. Deletion is AQR3's retraction flag and nothing computes it.
   AttainmentIndex is CAM_15's trailing ordering index: the guide says one attainment
   per zone/assessment regime unless an exceedance covers only part of the zone or
   different exceedances have different causes, and only an operator knows that. So the
   identifier is rebuilt on every run around whatever index is stored.

ONE ATTAINMENT PER REGIME PER YEAR. AttainmentId used to take a running row counter as
its ordering index, which made it a function of row position: the 2026-09-09 export gave
543 rows 543 AttainmentIds for 166 regimes, 444 of them with an index longer than the two
digits the guide allows, and adding one sampling point renumbered every row after it --
silently orphaning any PollutionLevelAdjustment an operator had typed against the old
value. It is now derived from the row's own AssessmentRegimeId, which carries the same
zone, pollutant, objective type, protection target and reporting metric by construction.
"""
import logging

from core.data.plans_programs_export import (SKIP_POLLUTANT_MISMATCH,
                                             PlansAndProgramsExport)
from core.eea.id_generator import get_or_validate_country_code

logger = logging.getLogger(__name__)

# Why a sampling point produced no compliance row. The codes the derivation raises
# (SKIP_POLLUTANT_MISMATCH and friends) travel through unchanged; these are the two this
# module decides for itself.
SKIP_INCOMPLETE_REGIME = 'incomplete_regime'
SKIP_DUPLICATE_KEY = 'duplicate_key'

# Human wording for the Dataflow page, so the toast and the panel cannot drift from the
# codes.
SKIP_LABELS = {
    SKIP_INCOMPLETE_REGIME: 'incomplete assessment regime',
    SKIP_DUPLICATE_KEY: 'another row already covers this regime, aggregation process '
                        'and assessment method',
    SKIP_POLLUTANT_MISMATCH: 'the sampling point measures a different pollutant than '
                             'its assessment regime',
}

# The evaluation reports isexceedance as a string; CAM_08 is a boolean.
_EXCEEDANCE_TRUE = {'yes', 'true', '1'}
_EXCEEDANCE_FALSE = {'no', 'false', '0'}

# The evaluation drives off sampling_points with a LEFT JOIN to assessmentdata, so
# a database with no assessment regimes yields one skipped row per sampling point —
# hundreds of near-identical entries returned to the Dataflow page. Report a sample
# and a total instead of the whole list.
#
# Stratified: up to this many PER REASON, not per run. A database missing its assessment
# regimes produces hundreds of `incomplete_regime` entries, which under a flat cap bury
# the handful of `pollutant_mismatch` ones — and those are the only kind an operator can
# act on row by row.
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

    # Rows the derivation itself refused -- a sampling point whose pollutant contradicts
    # its regime. They arrive already carrying a code and a reason.
    skipped = list(result.get('skipped', []))

    # Keyed up front, so the pre-delete below knows which rows are about to be
    # rebuilt and can leave them alone.
    planned, seen = [], {}
    for row in evaluated:
        regime_id = row.get('assessmentregimeid')
        method_id = row.get('assessmentmethodid')
        aggregation = row.get('dataaggregationprocessid')

        if not (regime_id and method_id and aggregation):
            skipped.append({
                'code': SKIP_INCOMPLETE_REGIME,
                'assessment_method_id': method_id,
                'assessment_regime_id': regime_id,
                'reason': 'incomplete assessment regime (missing regime id, '
                          'assessment method id or aggregation process)',
            })
            continue

        # The CAM primary key. Two assessmentdata rows linking one sampling point to one
        # regime under different assessment types collide here, and the upsert would run
        # twice for one row -- the second silently overwriting the first and `written`
        # counting both. First wins, and the loser is reported rather than dropped
        # quietly, because the two rows genuinely disagree about how the air was assessed
        # and only an operator can say which is right.
        key = (regime_id, aggregation, method_id)
        if key in seen:
            skipped.append({
                'code': SKIP_DUPLICATE_KEY,
                'assessment_method_id': method_id,
                'assessment_regime_id': regime_id,
                'reason': f'a row for {regime_id} / {aggregation} / {method_id} is '
                          f'already produced by assessment type '
                          f'{seen[key].get("assessmenttype")}; this one says '
                          f'{row.get("assessmenttype")}',
            })
            continue
        seen[key] = row

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
                %(relative_uncertainty_limit)s,
                COALESCE(%(assessment_mqi)s, %(assessment_mqi_seed)s), %(correction_flag)s,
                %(attainment_id)s, %(srs_id)s, %(preliminary_reason_id)s
            )
            ON CONFLICT (reporting_year, assessment_regime_id,
                         data_aggregation_process_id, assessment_method_id)
            DO UPDATE SET
                -- Derived: restated on every run, so a stale value cannot persist.
                pollutant_id               = EXCLUDED.pollutant_id,
                assessment_type_id         = EXCLUDED.assessment_type_id,
                -- Derived, but around a number the operator owns. The unqualified
                -- reference is the STORED index, so a regime an operator has split into
                -- an exceedance and a non-exceedance situation keeps that split; the
                -- proposed row cannot carry it, because it was built without seeing the
                -- database. See attainment_index below.
                attainment_id              = CASE
                                                 WHEN %(attainment_base)s IS NULL THEN NULL
                                                 ELSE %(attainment_base)s || '_' ||
                                                      compliance_assessment_method.attainment_index::text
                                             END,
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
                -- Three tiers, and the order is the whole meaning: a computed value
                -- wins, else what the operator typed, else the model's own GenericMQI
                -- (MOE_08). The seed is a property of the METHOD, while CAM_13 is the
                -- MQI of this assessment, so it is a sensible default and never a
                -- restatement -- passing it as EXCLUDED would have it beat a typed
                -- value on every run.
                assessment_mqi             = COALESCE(EXCLUDED.assessment_mqi,
                                                      compliance_assessment_method.assessment_mqi,
                                                      %(assessment_mqi_seed)s),
                correction_flag            = COALESCE(EXCLUDED.correction_flag,
                                                      compliance_assessment_method.correction_flag),
                preliminary_reason_id      = COALESCE(EXCLUDED.preliminary_reason_id,
                                                      compliance_assessment_method.preliminary_reason_id),
                -- CAM_16 joined this tier when it stopped being fabricated. Nothing can
                -- derive it: SRS_02 names an area an operator uploads, and SRS_06 points
                -- from that area at the model which assessed it, not at this row.
                srs_id                     = COALESCE(EXCLUDED.srs_id,
                                                      compliance_assessment_method.srs_id),
                -- `deletion` and `attainment_index` are absent on purpose. Both are
                -- the operator's, and both are NOT NULL with a default, which is exactly
                -- what COALESCE cannot protect: the proposed row carries the default
                -- rather than NULL, so it would win every time. Leaving them out of the
                -- statement entirely is the only way a recalculation cannot touch them;
                -- the column default covers a row being inserted for the first time.
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
            'assessment_mqi_seed': row.get('modelgenericmqi'),
            'correction_flag': _as_bool(row.get('correctionfactor')),
            'attainment_id': row.get('attainmentid'),
            # The identifier without its ordering index. Only the UPDATE half uses it —
            # on INSERT there is no stored index yet and the column default is 1, which
            # is what `attainmentid` already carries.
            'attainment_base': row.get('attainmentbase'),
            'srs_id': row.get('srsid'),
            'preliminary_reason_id': row.get('preliminaryreason'),
        })

    by_reason, sample = {}, []
    for entry in skipped:
        code = entry.get('code') or SKIP_INCOMPLETE_REGIME
        by_reason[code] = by_reason.get(code, 0) + 1
        if by_reason[code] <= _MAX_REPORTED_SKIPS:
            sample.append(entry)

    if skipped:
        logger.warning('CAM %s: skipped %s row(s) — %s', reporting_year, len(skipped),
                       ', '.join(f'{n} {SKIP_LABELS.get(code, code)}'
                                 for code, n in sorted(by_reason.items())))

    # A regime every one of whose rows was skipped reports no compliance at all while
    # still being declared in ARZ, which is the one outcome nobody notices from a count.
    # Naming them is what makes it fixable: the 2026-09-09 data has six such regimes, all
    # NOX-as-NO2 critical levels for vegetation assessed by NO2 sampling points.
    produced = {regime for _, regime, _, _ in planned}
    silenced = sorted({entry.get('assessment_regime_id')
                       for entry in skipped
                       if entry.get('assessment_regime_id')
                       and entry.get('assessment_regime_id') not in produced})

    summary = {
        'reporting_year': reporting_year,
        'evaluated': len(evaluated),
        'written': len(planned),
        'skipped_total': len(skipped),
        'skipped_by_reason': by_reason,
        'skipped_labels': {code: SKIP_LABELS.get(code, code) for code in by_reason},
        'skipped': sample,
        'out_of_scope': result.get('out_of_scope', 0),
        'regimes_without_rows': silenced,
    }

    # Nothing written with everything skipped is not a partial result — it means no
    # assessment regime covers these sampling points. Say so, rather than leaving a
    # zero that reads like a successful run.
    if evaluated and not planned:
        summary['message'] = (
            f'No compliance rows written for {reporting_year}: none of the '
            f'{len(evaluated)} evaluated sampling point(s) is linked to an assessment '
            f'regime. Define assessment regimes and link sampling points to them via '
            f'assessmentdata before reporting CAM.')

    return summary
