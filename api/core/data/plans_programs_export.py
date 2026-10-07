"""
Plans & Programs exceedances export logic.

This module transforms RAVEN exceedances data into EEA-compliant format
for integration with the Plans & Programs (Flow H-K) module.

The export:
1. Evaluates exceedances using existing RAVEN logic
2. Generates EEA-compliant IDs
3. Maps pollutants to EEA codes
4. Maps assessment types to EEA format
5. Includes context data for UI display
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from core.eea.id_generator import (
    EEAIDGenerator,
    IdentifierError,
    get_or_validate_country_code,
)
from core.data.exceedances import (
    Exceedances,
    DIRECTIVE_THRESHOLDS,
    get_pollutant_eea_code,
    map_assessment_type,
    resolve_aggregation_process,
)
from core.data.statistics import Statistics

logger = logging.getLogger(__name__)


# Why a sampling point produced no compliance row. `None` already meant "formatting
# threw", and folding a deliberate exclusion in with a crash loses the one thing an
# operator can act on -- so a skip says which kind it is, and persist_compliance groups
# the summary by it.
# Is this sampling point part of the EEA reporting obligation at all?
#
# The same conjunction core/reporting/aqr3/spec.py applies to SPO, SPL, SPP and OMR --
# the operator's decision (report_to_eea, migration 022) AND the identifiers AQR3 needs
# to name the row. Spelled out here rather than imported, because the two modules own
# different halves of the rule: spec.py filters what is EXPORTED, and CAM's own export
# spec deliberately cannot -- compliance_assessment_method has no report_to_eea column
# and must not gain one (tests/unit/test_aqr3_registry.py pins that). So scope has to be
# applied here, when the row is DERIVED, or CAM ends up referencing sampling points that
# SamplingPoint.csv no longer contains.
_IN_SCOPE = ('sp.report_to_eea AND st.report_to_eea '
             'AND sp.pollutant_id > 0 AND st.station_eoi_code IS NOT NULL')

# Was this method assessing this regime during the reporting year?
#
# NULL on either bound reads as unbounded, which is what makes a link written before
# 4.502.24 -- when assessmentdata gained a period at all -- still match every year. The
# same shape the query already applies to the sampling point's own validity window, so
# the two read alike. Without it, recalculating 2019 uses today's links and an earlier
# submission cannot be reproduced.
_LINK_IN_PERIOD = (
    '(ad.from_time IS NULL OR ad.from_time <= %(reportingyear_end)s::timestamp) '
    'AND (ad.to_time IS NULL OR ad.to_time >= %(reportingyear_start)s::timestamp)')

SKIP_POLLUTANT_MISMATCH = 'pollutant_mismatch'
SKIP_MALFORMED_REGIME = 'malformed_regime_id'
SKIP_FORMAT_FAILED = 'format_failed'


class Skipped:
    """A row the derivation deliberately did not produce, and why."""

    __slots__ = ('code', 'reason', 'assessment_method_id', 'assessment_regime_id')

    def __init__(self, code, reason, assessment_method_id=None,
                 assessment_regime_id=None):
        self.code = code
        self.reason = reason
        self.assessment_method_id = assessment_method_id
        self.assessment_regime_id = assessment_regime_id

    def as_dict(self):
        return {'code': self.code, 'reason': self.reason,
                'assessment_method_id': self.assessment_method_id,
                'assessment_regime_id': self.assessment_regime_id}


class PlansAndProgramsExport:
    """Export exceedances in Plans & Programs EEA-compliant format."""
    
    def __init__(self, cursor):
        """
        Initialize exporter.
        
        Args:
            cursor: Database cursor (psycopg2)
        """
        self.cursor = cursor
        self.exceedances = Exceedances(cursor)
        self.statistics = Statistics(cursor)
        self.id_generator = EEAIDGenerator()
    
    def export_exceedances(
        self,
        countrycode: Optional[str],
        reportingyear: int,
        directive: str = "2024/2881",
        pollutants: List[str] = None,
        zones: List[str] = None,
        exceedances_only: bool = True,
        assessment_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Export exceedances formatted for Plans & Programs.
        
        Args:
            countrycode: ISO 2-letter country code (or None to use settings)
            reportingyear: Year to evaluate
            directive: EU directive ('2008/50', '2024/2881', 'WHO')
            pollutants: Filter by pollutant notations (empty = all)
            zones: Filter by zone IDs (empty = all)
            exceedances_only: Only return exceeded thresholds
            assessment_types: Filter by assessment type (empty = all)
        
        Returns:
            Dictionary with metadata and formatted exceedances array
        """
        # Get and validate country code
        validated_country_code = get_or_validate_country_code(
            self.cursor,
            countrycode
        )
        
        # Query exceedances with full context
        exceedances_data, out_of_scope = self._query_exceedances(
            countrycode=validated_country_code,
            reportingyear=reportingyear,
            directive=directive,
            pollutants=pollutants or [],
            zones=zones or [],
            exceedances_only=exceedances_only,
            assessment_types=assessment_types or []
        )
        
        # Transform to EEA format.
        #
        # No running counter any more. It used to be passed in as the AttainmentId's
        # ordering index, which made the identifier a function of row position: the
        # 2026-09-09 export gave 543 rows 543 AttainmentIds for 166 regimes, and adding
        # one sampling point renumbered every row after it. CAM_15 is now derived from
        # the row's own AssessmentRegimeId in _format_exceedance.
        formatted_exceedances = []
        skipped = []

        for row in exceedances_data:
            formatted = self._format_exceedance(
                row,
                validated_country_code,
                reportingyear,
                directive
            )
            if isinstance(formatted, Skipped):
                skipped.append(formatted)
            elif formatted:  # None means formatting threw; it is logged there
                formatted_exceedances.append(formatted)
        
        # Generate metadata
        metadata = self._generate_metadata(
            validated_country_code,
            reportingyear,
            directive,
            formatted_exceedances
        )
        
        # Generate zone summaries
        zone_summaries = self._generate_zone_summaries(formatted_exceedances)
        
        # `skipped` and `out_of_scope` are additive: the raven-plan-program wizard reads
        # `metadata` and `exceedances` with .get() and ignores what it does not know.
        return {
            "success": True,
            "metadata": metadata,
            "exceedances": formatted_exceedances,
            "zone_summaries": zone_summaries,
            "skipped": [s.as_dict() for s in skipped],
            "out_of_scope": out_of_scope,
        }
    
    def _query_exceedances(
        self,
        countrycode: str,
        reportingyear: int,
        directive: str,
        pollutants: List[str],
        zones: List[str],
        exceedances_only: bool,
        assessment_types: List[str]
    ) -> List[Dict]:
        """
        Query database for exceedances with full context.
        
        Uses spatial join for zones and includes all metadata needed
        for EEA format transformation.
        """
        # Build WHERE clauses
        where_clauses = []
        params = {
            'reportingyear': reportingyear,
            'reportingyear_start': f'{reportingyear}-01-01 00:00:00',
            'reportingyear_end': f'{reportingyear}-12-31 23:59:59'
        }
        
        # Filter by pollutants if specified
        if pollutants:
            where_clauses.append("p.notation = ANY(%(pollutants)s)")
            params['pollutants'] = pollutants
        
        # Filter by zones if specified
        if zones:
            where_clauses.append("z.id = ANY(%(zones)s)")
            params['zones'] = zones
        
        # Filter by assessment types if specified
        if assessment_types:
            # Map back to RAVEN notations
            raven_notations = [
                k for k, v in map_assessment_type.__globals__.get('ASSESSMENT_TYPE_MAPPING', {}).items()
                if v in assessment_types
            ]
            if raven_notations:
                where_clauses.append("eat.notation = ANY(%(assessment_types)s)")
                params['assessment_types'] = raven_notations
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Main query with spatial join for zones
        # v4 schema: assessment_type is on assessmentdata, zones have no year
        # v4 schema: stations have latitude/longitude columns directly (not PostGIS geom)
        # v4 schema: processes table doesn't have uncertainty_estimate/detection_limit
        def build(scope_sql, models_sql='true'):
            """The two branches of the row set, ordered as one.

            A UNION cannot carry per-branch ordering, so the union is wrapped and the
            ORDER BY applied to the whole -- which also means it names output aliases
            rather than table columns.
            """
            return f"""
        SELECT * FROM (
        SELECT 
            -- Sampling point & station
            sp.id as sampling_point_id,
            sp.id as sampling_point_code,
            st.name as station_name,
            st.station_eoi_code as station_code,
            st.longitude as longitude,
            st.latitude as latitude,
            
            -- Zone (via assessment_regimes) - v4 schema
            z.id as zone_id,
            z.zone_national_code as zone_code,
            z.name as zone_name,
            zc.notation as zone_category,

            -- Assessment regime. ar.id IS the AQR3 AssessmentRegimeId (ARZ_02) and
            -- already carries the mandatory ARE_ format, so it is read, not rebuilt.
            -- The component notations are what AttainmentId (CAM_15) is built from.
            ar.id as assessment_regime_id,
            -- COALESCE to the id because sql/data.sql seeds these three vocabularies as
            -- (id, label, uri) only, leaving notation NULL on a fresh install. The id is
            -- the short EEA code under the v4 convention, so it is the same string.
            -- Without this, objective_type and reporting_metric arrive as None and
            -- DataAggregationProcessId cannot be resolved for any row.
            COALESCE(NULLIF(ot.notation, ''), ot.id) as objective_type,
            COALESCE(NULLIF(pt.notation, ''), pt.id) as protection_target,
            COALESCE(NULLIF(rm.notation, ''), rm.id) as reporting_metric,
            
            -- Pollutant. AQR3 PollutantId is the numeric code, not the notation.
            --
            -- Both are selected because they can disagree. CAM_06 and the AttainmentId
            -- come from the REGIME -- that is what AQR3 files the compliance situation
            -- under, and ARZ reports the same number -- while the sampling point's is
            -- what the instrument actually measures. 12 of the 543 rows in the
            -- 2026-09-09 export reported PollutantId 8 (NO2) under a regime for
            -- pollutant 9 (NOX as NO2). _format_exceedance skips those and names both,
            -- because filing NO2 measurements under a NOX regime is a false statement
            -- about what was assessed, and only somebody looking at the link can fix it.
            ar.pollutant_id as regime_pollutant_id,
            COALESCE(NULLIF(rp.notation, ''), rp.label) as regime_pollutant,
            rp.label as regime_pollutant_label,
            rp.uri as regime_pollutant_uri,
            p.id as pollutant_id,
            p.notation as pollutant,
            p.label as pollutant_label,
            p.uri as pollutant_uri,
            
            -- Network
            n.name as network_name,
            n.id as network_id,
            
            -- Assessment type (from assessmentdata in v4 schema)
            eat.notation as assessment_type_notation,
            eat.label as assessment_type_label,

            -- AQR3 MOE_08 GenericMQI, for the model branch below. NULL here: a sampling
            -- point has no modelling quality indicator, and CAM_12 is its analogue.
            NULL::numeric as model_generic_mqi

        FROM sampling_points sp
        JOIN stations st ON sp.station_id = st.id
        JOIN eea_pollutants p ON sp.pollutant_id = p.id
        JOIN networks n ON st.network_id = n.id
        -- v4: assessment_type is on assessmentdata, not sampling_points
        LEFT JOIN assessmentdata ad ON ad.sampling_point_id = sp.id
        LEFT JOIN eea_assessmenttypes eat ON ad.assessmenttype = eat.id
        -- v4: zones have no year column, join via assessment_regimes
        LEFT JOIN assessment_regimes ar ON ad.assessment_regime_id = ar.id
        LEFT JOIN zones z ON ar.zone_id = z.id
        LEFT JOIN eea_zonecategory zc ON z.zone_category_id = zc.id
        LEFT JOIN eea_objectivetypes ot ON ar.objective_type_id = ot.id
        LEFT JOIN eea_protectiontargets pt ON ar.protection_target_id = pt.id
        LEFT JOIN eea_reportingmetrics rm ON ar.reporting_metric_id = rm.id
        LEFT JOIN eea_pollutants rp ON ar.pollutant_id = rp.id
        
        WHERE 1=1
          AND sp.from_time <= %(reportingyear_end)s::timestamp
          AND (sp.to_time IS NULL OR sp.to_time >= %(reportingyear_start)s::timestamp)
          AND {_LINK_IN_PERIOD}
          AND {scope_sql}
          AND {where_sql}
        
        UNION ALL

        -- The same regimes, assessed by a model or objective estimation rather than by
        -- an instrument. AQR3 CAM_05 is "either a sampling_points.id or a models.id",
        -- and until 4.502.24 the link table could hold only the first, so a zone
        -- assessed by modelling reported no compliance at all.
        --
        -- A model has no station, no network, no location and no validity window of its
        -- own, so those columns are NULL here -- but they are still SELECTed, in the
        -- same order and with the same casts, because a UNION matches columns by
        -- position. The nested station dict downstream stays a dict with null fields
        -- rather than becoming None: the raven-plan-program wizard reads it as
        -- exc.get('station', {{}}).get('name'), which a None would turn into an
        -- AttributeError.
        --
        -- AssessmentType comes from the link, not from the id prefix. An OBE_ model is
        -- usually 'objective' and a MOD_ one 'model', but which it is for this regime is
        -- something the operator records; guessing it would repeat the defect
        -- map_assessment_type was written to stop.
        --
        -- DataAggregationProcessId is NOT models.data_aggregation_process_id. That is
        -- MOE_03, describing what the model outputs; CAM_04 names the statistic AND the
        -- threshold level it is assessed against, which is directive-specific and comes
        -- from the regime.
        SELECT
            m.id as sampling_point_id,
            m.id as sampling_point_code,
            NULL::varchar as station_name,
            NULL::varchar as station_code,
            NULL::numeric as longitude,
            NULL::numeric as latitude,

            z.id as zone_id,
            z.zone_national_code as zone_code,
            z.name as zone_name,
            zc.notation as zone_category,

            ar.id as assessment_regime_id,
            COALESCE(NULLIF(ot.notation, ''), ot.id) as objective_type,
            COALESCE(NULLIF(pt.notation, ''), pt.id) as protection_target,
            COALESCE(NULLIF(rm.notation, ''), rm.id) as reporting_metric,

            ar.pollutant_id as regime_pollutant_id,
            COALESCE(NULLIF(rp.notation, ''), rp.label) as regime_pollutant,
            rp.label as regime_pollutant_label,
            rp.uri as regime_pollutant_uri,
            m.pollutant_id as pollutant_id,
            -- Aliased `p` to match the measurement branch: the caller's pollutant
            -- filter is interpolated into both branches as `p.notation = ANY(...)`.
            COALESCE(NULLIF(p.notation, ''), p.label) as pollutant,
            p.label as pollutant_label,
            p.uri as pollutant_uri,

            NULL::varchar as network_name,
            -- varchar, not integer: networks.id is varchar(100) in v4, and the
            -- measurement branch above selects n.id directly. An integer cast here
            -- makes the whole UNION fail with "types character varying and integer
            -- cannot be matched", which takes compliance recalculation -- and so
            -- the entire CAM table -- down with it.
            NULL::varchar as network_id,

            eat.notation as assessment_type_notation,
            eat.label as assessment_type_label,

            -- MOE_08. A property of the method, so only a DEFAULT for CAM_13, which is
            -- the MQI of this assessment -- this regime, this pollutant, this year.
            -- persist_compliance puts it below anything typed, never above.
            m.generic_mqi as model_generic_mqi

        FROM models m
        JOIN assessmentdata ad ON ad.model_id = m.id
        JOIN assessment_regimes ar ON ad.assessment_regime_id = ar.id
        LEFT JOIN eea_assessmenttypes eat ON ad.assessmenttype = eat.id
        LEFT JOIN zones z ON ar.zone_id = z.id
        LEFT JOIN eea_zonecategory zc ON z.zone_category_id = zc.id
        LEFT JOIN eea_objectivetypes ot ON ar.objective_type_id = ot.id
        LEFT JOIN eea_protectiontargets pt ON ar.protection_target_id = pt.id
        LEFT JOIN eea_reportingmetrics rm ON ar.reporting_metric_id = rm.id
        LEFT JOIN eea_pollutants rp ON ar.pollutant_id = rp.id
        LEFT JOIN eea_pollutants p ON m.pollutant_id = p.id

        WHERE 1=1
          AND {_LINK_IN_PERIOD}
          -- `models` has no report_to_eea column and must not gain one, so the scope
          -- predicate does not apply here; a model exists only because somebody added
          -- it for reporting. The pollutant half still does: a CAM row whose
          -- PollutantId is not a real EEA code is dropped at export without a word.
          AND m.pollutant_id > 0
          AND {models_sql}
          AND {where_sql}
        ) rows

        -- Deterministic to the last column. The AttainmentId no longer depends on row
        -- position, but the winner of a duplicate key in persist_compliance does, and
        -- "the first one" has to mean the same row on every run.
        ORDER BY zone_code, pollutant, assessment_regime_id, sampling_point_id,
                 assessment_type_notation
        """

        self.cursor.execute(build(_IN_SCOPE), params)
        rows = self.cursor.fetchall()

        # The same row set with the scope predicate negated, counted rather than
        # returned: a recalculation that quietly produces fewer rows than last time is
        # worse than one that says how many sampling points it left out and why. Sharing
        # the query text is what keeps the two halves in step.
        excluded = build(f'NOT ({_IN_SCOPE})', models_sql='false')
        self.cursor.execute(f'SELECT count(*) AS n FROM ({excluded}) excluded', params)
        out_of_scope = self.cursor.fetchone()['n']

        return rows, out_of_scope
    
    def _format_exceedance(
        self,
        row: Dict,
        countrycode: str,
        reportingyear: int,
        directive: str
    ) -> Optional[Dict]:
        """
        Format a single exceedance row to EEA structure.

        Returns a `Skipped` when the row is deliberately not produced, and None when
        formatting threw. Those are different answers and used to be the same one.
        """
        try:
            assessment_regime_id = row.get('assessment_regime_id')
            method_id = row.get('sampling_point_id')

            # AQR3 files a compliance situation under an assessment regime, and the
            # regime names the pollutant it assesses. A sampling point measuring
            # something else is a broken link, not a compliance result -- reporting it
            # would state that pollutant X was assessed under a regime for pollutant Y.
            # Named on both sides, because fixing it means looking at the link.
            regime_pollutant_id = row.get('regime_pollutant_id')
            if (regime_pollutant_id is not None
                    and row.get('pollutant_id') is not None
                    and int(regime_pollutant_id) != int(row['pollutant_id'])):
                return Skipped(
                    SKIP_POLLUTANT_MISMATCH,
                    f"sampling point measures {row.get('pollutant')} "
                    f"(PollutantId {row['pollutant_id']}) but is linked to "
                    f"{assessment_regime_id}, a regime for "
                    f"{row.get('regime_pollutant')} (PollutantId {regime_pollutant_id}). "
                    f"Correct the link on Management -> Assessment Data, or the "
                    f"regime's pollutant.",
                    method_id, assessment_regime_id)

            # Past the check the two agree, so either would do -- but the regime's is the
            # one AQR3 reports and the one the identifiers are built from, so it is the
            # one read.
            pollutant = row.get('regime_pollutant') or row['pollutant']
            pollutant_id = regime_pollutant_id if regime_pollutant_id is not None                 else row.get('pollutant_id')
            zone_code = row.get('zone_code') or row.get('zone_id') or 'UNKNOWN'
            zone_name = row.get('zone_name') or zone_code

            # AQR3 v5.02 identifiers.
            #
            # AssessmentRegimeId already exists on the regime row in its mandatory ARE_
            # format, so it is read rather than rebuilt. AssessmentMethodId is simply the
            # sampling point id (CAM_05).
            #
            # AttainmentId is the same identifier with the classification year swapped
            # for the reporting year, so it too is read off the regime rather than
            # recomposed from the regime's component columns -- those can render
            # differently here than they did when the regime id was built, because this
            # query COALESCEs a missing notation to the id and _derive_id does not.
            #
            # `attainmentbase` is the identifier without its trailing ordering index.
            # persist_compliance appends the index stored on the row, so that an operator
            # who has split a regime into an exceedance and a non-exceedance situation
            # keeps that split across a recalculation. Over HTTP there is no stored row
            # to consult, so `attainmentid` is the index-1 form.
            assessment_method_id = method_id

            attainment_base = attainment_id = None
            if assessment_regime_id:
                try:
                    attainment_base = self.id_generator.attainment_base(
                        assessment_regime_id, reportingyear)
                    attainment_id = self.id_generator.attainment_id_from_regime(
                        assessment_regime_id, reportingyear)
                except IdentifierError as e:
                    # A regime that predates ARZ_02 validation cannot yield a conformant
                    # AttainmentId. Surface it rather than emitting a bad one.
                    logger.warning('No AttainmentId for sampling point %s: %s',
                                   method_id, e)

            # CAM_16 is NOT the assessment method. SRS_02 identifies a spatial
            # representativeness area an operator uploads on Management -> Spatial
            # Representativeness, and SRS_06 points from that area at the model which
            # assessed it -- so nothing here can derive the link. Setting it to the
            # sampling point id pointed all 214 distinct SRSIds in the 2026-09-09 export
            # at a SpatialRepresentativeness.csv with no rows in it. It is entered on the
            # CAM screen now, and preserved across a recalculation by persist_compliance.
            srs_id = None

            # Get EEA pollutant code
            air_pollutant_code = get_pollutant_eea_code(pollutant)
            
            # Map assessment type
            assessment_type = map_assessment_type(row.get('assessment_type_notation', ''))

            # AQR3 CAM_04. The regime's ReportingMetric says what is measured; the
            # aggregation process says what is measured and against which level, and
            # the level moved between directives. Unresolved means this row is skipped
            # by persist_compliance and counted, rather than filed under a statistic
            # that was never calculated.
            aggregation_process = resolve_aggregation_process(
                pollutant, row.get('objective_type'), row.get('reporting_metric'),
                directive)
            
            # For now, create a placeholder structure
            # TODO: Integrate with actual exceedance evaluation
            # This will be enhanced to pull real aggregated values
            
            return {
                # EEA Compliance Structure
                "countrycode": countrycode,
                "assessmentregimeid": assessment_regime_id,
                "dataaggregationprocessid": aggregation_process,
                "assessmentmethodid": assessment_method_id,
                # AQR3 v5.02 renamed these two. The pre-v5.02 keys `complianceid`
                # and `airpollutantcode` are gone: compliance keys on AttainmentId,
                # and PollutantId is the numeric code.
                "reportingyear": reportingyear,
                # The regime's, not the sampling point's -- see the mismatch check above.
                "pollutantid": pollutant_id,
                "assessmenttype": assessment_type,
                "hotspot": False,
                "isexceedance": "unknown",  # TODO: Calculate from threshold evaluation
                "airpollutionlevel": None,  # TODO: Get from aggregation
                "airpollutionleveladjusted": None,
                # Always None: `processes` lost its uncertainty_estimate column in v4 and
                # the query has not selected it since. Kept as a key because the HTTP
                # payload is a contract.
                "absoluteuncertaintylimit": None,
                "relativeuncertaintylimit": None,
                "maxratiouncertainty": None,
                # None, not False: CAM_14 is entered by hand until the evaluation
                # computes it, and persist_compliance keeps a stored value only while
                # the computed one is NULL. A placeholder False would win every time.
                "correctionfactor": None,
                "attainmentid": attainment_id,
                # The identifier without its ordering index; persist_compliance appends
                # the index stored on the row. Additive -- no HTTP consumer reads it.
                "attainmentbase": attainment_base,
                # NOT `assessmentmqi`. That key feeds EXCLUDED.assessment_mqi, which
                # wins over a stored value on every recalculation -- exactly the trap
                # the `correctionfactor` placeholder was fixed for. This is a seed:
                # persist_compliance uses it only when nothing else has a value.
                "modelgenericmqi": row.get('model_generic_mqi'),
                "srsid": srs_id,
                "preliminaryreason": None,
                
                # Nested context for UI display (expected by raven-plan-program import)
                "zone": {
                    "id": row.get('zone_id'),
                    "code": zone_code,
                    "name": zone_name,
                    "category": row.get('zone_category'),
                    "inspireId": f"{countrycode}.AQ.ZONE.{zone_code}" if zone_code else None
                },
                "station": {
                    "name": row['station_name'],
                    "code": row['station_code'],
                    "station_eoi_code": row['station_code'],
                    "inspireId": f"{countrycode}.AQ.STATION.{row['station_code']}" if row.get('station_code') else None,
                    "longitude": float(row['longitude']) if row.get('longitude') else None,
                    "latitude": float(row['latitude']) if row.get('latitude') else None
                },
                "pollutant": {
                    "notation": pollutant,
                    "label": row.get('regime_pollutant_label') or row['pollutant_label'],
                    "eea_code": air_pollutant_code
                },
                "threshold": {
                    "objective": None,  # TODO: Get from threshold data
                    "objectivetype": None,
                    "value": None,
                    "unit": "µg/m³",
                    "operator": ">",
                    "directive": directive
                },
                "measurement": {
                    "value": None,  # TODO: Get from aggregation
                    "coverage": None,
                    "exceeded_by": None,
                    "exceeded_by_percent": None
                },
                "network": {
                    "name": row['network_name'],
                    "id": row['network_id']
                }
            }
        
        except Exception:
            # Log and continue: one malformed row must not cost the whole recalculation.
            # logger, not print -- in a container print goes nowhere anybody reads.
            logger.exception('Error formatting exceedance for sampling point %s',
                             row.get('sampling_point_id'))
            return None
    
    def _generate_metadata(
        self,
        countrycode: str,
        reportingyear: int,
        directive: str,
        exceedances: List[Dict]
    ) -> Dict:
        """Generate response metadata."""
        pollutants_exceeded = list(set([
            exc['pollutant']['notation']
            for exc in exceedances
            if exc.get('isexceedance') == 'yes'
        ]))
        
        zones_affected = len(set([
            exc['zone']['code']
            for exc in exceedances
            if exc.get('isexceedance') == 'yes' and exc.get('zone', {}).get('code')
        ]))
        
        return {
            "countrycode": countrycode,
            "reportingyear": reportingyear,
            "directive": directive,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_exceedances": len([e for e in exceedances if e.get('isexceedance') == 'yes']),
            "total_evaluated": len(exceedances),
            "zones_affected": zones_affected,
            "pollutants_exceeded": sorted(pollutants_exceeded)
        }
    
    def _generate_zone_summaries(self, exceedances: List[Dict]) -> List[Dict]:
        """Generate zone-level summaries."""
        zones = {}
        
        for exc in exceedances:
            if exc.get('isexceedance') != 'yes':
                continue
            
            zone_code = exc.get('zone', {}).get('code')
            if not zone_code or zone_code == 'UNKNOWN':
                continue
            
            if zone_code not in zones:
                zones[zone_code] = {
                    "zoneid": exc.get('zone', {}).get('id'),
                    "zonename": exc.get('zone', {}).get('name'),
                    "exceedances_count": 0,
                    "pollutants": set(),
                    "worst_exceedance": None
                }
            
            zone = zones[zone_code]
            zone['exceedances_count'] += 1
            zone['pollutants'].add(exc.get('pollutant', {}).get('notation'))
            
            # Track worst exceedance
            exceeded_by_pct = exc.get('measurement', {}).get('exceeded_by_percent')
            if exceeded_by_pct and (zone['worst_exceedance'] is None or 
                                    exceeded_by_pct > zone['worst_exceedance'].get('exceeded_by_percent', 0)):
                zone['worst_exceedance'] = {
                    "pollutant": exc.get('pollutant', {}).get('notation'),
                    "value": exc.get('airpollutionlevel'),
                    "threshold": exc.get('threshold', {}).get('value'),
                    "exceeded_by_percent": exceeded_by_pct
                }
        
        # Convert sets to sorted lists
        for zone in zones.values():
            zone['pollutants'] = sorted(list(zone['pollutants']))
        
        return list(zones.values())
