"""AQR3 v5.02 reporting-table registry.

One declarative entry per CSV table: the exact column headers from the reporting
guide, the SQL that produces them, and the formatter for each value. The route
handlers, the ZIP builder and the Vue export list are all driven from here, so
adding a table is one entry rather than a function plus a route plus a service
method plus a hardcoded frontend row.

Column names are the attribute names from the guide's `Attributes` sheet, which
is normative. Where a per-table `example` sheet disagrees (`SamplingPointReferenceID`
for SPO_03, `Building Distance` for SPL_13) the Attributes sheet wins — the
example sheets contain other clear slips such as `Attainment d` and `Scenari Year`.

Out of scope here: CPL, PSC, SAP, SME, MEA (the old H-K plans and programmes
flows, owned by raven-plan-program) and OMP (PNSD, deferred — the guide's own
example is still "to be developed").
"""
from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple

from core.reporting.aqr3 import formatters as f


@dataclass(frozen=True)
class Column:
    """One CSV column: its AQR3 header, the SQL result key, how to format it."""
    name: str
    source: str
    fmt: Optional[Callable] = None

    def render(self, row, ctx):
        value = row.get(self.source)
        if self.fmt is None:
            return f.text(value)
        # datetime formatters are built per-request from the timezone offset
        if self.fmt is DATETIME:
            return f.datetime_with(ctx.timezone_offset)(value)
        return self.fmt(value)


# Sentinel: resolved per-request in Column.render because it depends on ctx.
DATETIME = object()


@dataclass(frozen=True)
class TableSpec:
    code: str
    name: str
    sql: str
    columns: Tuple[Column, ...]
    description: str = ''
    year_dependent: bool = False
    params: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def filename(self):
        return f'{self.name}.csv'

    def headers(self):
        return [c.name for c in self.columns]


# --------------------------------------------------------------------------
# 1 AUT Authority
# --------------------------------------------------------------------------
AUT = TableSpec(
    code='AUT', name='Authority',
    description='Contact details of the responsible authorities and their area of responsibility.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s          AS country_code,
               a.id                      AS authority_instance_id,
               ar.notation               AS authority_role,
               a.email,
               ai.notation               AS authority_instance,
               a.authority_name,
               a.authority_url,
               a.authority_address,
               a.person_name,
               ast.notation              AS authority_status
        FROM authorities a
        LEFT JOIN eea_authorityobject   ar  ON a.authority_role_id     = ar.id
        LEFT JOIN eea_authorityinstance ai  ON a.authority_instance_id = ai.id
        LEFT JOIN eea_authoritystatus   ast ON a.authority_status_id   = ast.id
        ORDER BY a.id, ar.notation, a.email
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AuthorityInstanceId', 'authority_instance_id'),
        Column('AuthorityRole', 'authority_role'),
        Column('Email', 'email'),
        Column('AuthorityInstance', 'authority_instance'),
        Column('AuthorityName', 'authority_name'),
        Column('AuthorityURL', 'authority_url'),
        Column('AuthorityAddress', 'authority_address'),
        Column('PersonName', 'person_name'),
        Column('AuthorityStatus', 'authority_status'),
    ),
)

# --------------------------------------------------------------------------
# 2 STA MeasurementStation
#
# Denormalises the network onto each station row, as AQR3 requires. Timezone is
# the network's (STA_06), not the instance-wide settings value the old export used.
# --------------------------------------------------------------------------
STA = TableSpec(
    code='STA', name='MeasurementStation',
    description='Air quality measuring stations: EoI codes, names, the networks they belong to and the timezone those networks operate in.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s        AS country_code,
               st.station_eoi_code,
               n.id                    AS network_id,
               n.name                  AS network_name,
               al.notation             AS network_organisational_level,
               tz.notation             AS timezone,
               st.station_national_code,
               st.name                 AS station_name,
               n.network_document_id
        FROM stations st
        JOIN networks n ON st.network_id = n.id
        LEFT JOIN eea_administrativelevels al ON n.network_organisational_level_id = al.id
        LEFT JOIN eea_timezones tz            ON n.timezone_id = tz.id
        ORDER BY st.station_eoi_code
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('StationEoICode', 'station_eoi_code'),
        Column('NetworkId', 'network_id'),
        Column('NetworkName', 'network_name'),
        Column('NetworkOrganisationalLevel', 'network_organisational_level'),
        Column('Timezone', 'timezone'),
        Column('StationNationalCode', 'station_national_code'),
        Column('StationName', 'station_name'),
        Column('NetworkDocumentId', 'network_document_id'),
    ),
)

# --------------------------------------------------------------------------
# 3 SPO SamplingPoint
#
# Deliberately narrow: it only links AssessmentMethodId, SamplingPointReferenceId
# and StationEoICode. Location lives in SPL.
# --------------------------------------------------------------------------
SPO = TableSpec(
    code='SPO', name='SamplingPoint',
    description='Links each AssessmentMethodId to its SamplingPointReferenceId, pollutant and station EoI code.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               sp.id            AS assessment_method_id,
               sp.sampling_point_reference_id,
               sp.pollutant_id,
               st.station_eoi_code
        FROM sampling_points sp
        JOIN stations st ON sp.station_id = st.id
        ORDER BY sp.id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('SamplingPointReferenceId', 'sampling_point_reference_id'),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('StationEoICode', 'station_eoi_code'),
    ),
)

# --------------------------------------------------------------------------
# 4 SPL SamplingPointLocation
#
# sampling_point_locations holds per-period overrides only, so LEFT JOIN it and
# COALESCE down to the operational values on sampling_points/stations. With no
# override rows every sampling point still reports one complete location row,
# using sampling_points.from_time as LocationBegin.
# --------------------------------------------------------------------------
SPL = TableSpec(
    code='SPL', name='SamplingPointLocation',
    description='Where each sampling point is: coordinates, area and location characteristics, with the period each set of values applies to.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               sp.id            AS assessment_method_id,
               COALESCE(spl.location_begin, sp.from_time) AS location_begin,
               COALESCE(spl.location_end,   sp.to_time)   AS location_end,
               COALESCE(spl_ac.notation, st_ac.notation)  AS station_area,
               COALESCE(spl_sc.notation, sp_sc.notation)  AS sampling_point_category,
               COALESCE(spl.hotspot,   sp.hotspot)        AS hotspot,
               COALESCE(spl.supersite, st.supersite)      AS supersite,
               COALESCE(spl.latitude,  st.latitude)       AS latitude,
               COALESCE(spl.longitude, st.longitude)      AS longitude,
               COALESCE(spl.altitude,  st.altitude)       AS altitude,
               COALESCE(spl.inlet_height,             sp.inlet_height)             AS inlet_height,
               COALESCE(spl.building_distance,        sp.building_distance)        AS building_distance,
               COALESCE(spl.kerb_distance,            sp.kerb_distance)            AS kerb_distance,
               COALESCE(spl.emission_source_distance, sp.emission_source_distance) AS emission_source_distance
        FROM sampling_points sp
        JOIN stations st ON sp.station_id = st.id
        LEFT JOIN sampling_point_locations spl ON spl.sampling_point_id = sp.id
        LEFT JOIN eea_areaclassifications st_ac  ON st.station_area_id  = st_ac.id
        LEFT JOIN eea_areaclassifications spl_ac ON spl.station_area_id = spl_ac.id
        LEFT JOIN eea_spocategory sp_sc  ON sp.sampling_point_category_id  = sp_sc.id
        LEFT JOIN eea_spocategory spl_sc ON spl.sampling_point_category_id = spl_sc.id
        ORDER BY sp.id, COALESCE(spl.location_begin, sp.from_time)
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('LocationBegin', 'location_begin', DATETIME),
        Column('LocationEnd', 'location_end', DATETIME),
        Column('StationArea', 'station_area'),
        Column('SamplingPointCategory', 'sampling_point_category'),
        Column('Hotspot', 'hotspot', f.boolean),
        Column('Supersite', 'supersite', f.boolean),
        Column('Latitude', 'latitude', f.coordinate),
        Column('Longitude', 'longitude', f.coordinate),
        Column('Altitude', 'altitude', f.metres),
        Column('InletHeight', 'inlet_height', f.metres),
        Column('BuildingDistance', 'building_distance', f.metres),
        Column('KerbDistance', 'kerb_distance', f.metres),
        Column('EmissionSourceDistance', 'emission_source_distance', f.metres),
    ),
)

# --------------------------------------------------------------------------
# 5 SPP SamplingProcess
# --------------------------------------------------------------------------
SPP = TableSpec(
    code='SPP', name='SamplingProcess',
    description='Measurement techniques and methodologies: equipment configuration, quality information and operational periods.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               p.id             AS process_id,
               p.sampling_point_id AS assessment_method_id,
               p.process_activity_begin,
               p.process_activity_end,
               sp.pollutant_id,
               mt.notation      AS measurement_type,
               mm.notation      AS method,
               me.notation      AS equipment,
               at.notation      AS analytical_technique,
               ed.notation      AS equivalence_demonstrated,
               p.data_quality_document_id,
               p.equivalence_demonstration_document_id,
               p.process_document_id
        FROM processes p
        JOIN sampling_points sp ON p.sampling_point_id = sp.id
        LEFT JOIN eea_measurementtypes        mt ON p.measurement_type_id          = mt.id
        LEFT JOIN eea_measurementmethods      mm ON p.method_id                    = mm.id
        LEFT JOIN eea_measurementequipments   me ON p.equipment_id                 = me.id
        LEFT JOIN eea_analyticaltechnique     at ON p.analytical_technique_id      = at.id
        LEFT JOIN eea_equivalencedemonstrated ed ON p.equivalence_demonstrated_id  = ed.id
        ORDER BY p.id, p.process_activity_begin
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('ProcessId', 'process_id'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('ProcessActivityBegin', 'process_activity_begin', DATETIME),
        Column('ProcessActivityEnd', 'process_activity_end', DATETIME),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('MeasurementType', 'measurement_type'),
        Column('Method', 'method'),
        Column('Equipment', 'equipment'),
        Column('AnalyticalTechnique', 'analytical_technique'),
        Column('EquivalenceDemonstrated', 'equivalence_demonstrated'),
        Column('DataQualityDocumentId', 'data_quality_document_id'),
        Column('EquivalenceDemonstrationDocumentId', 'equivalence_demonstration_document_id'),
        Column('ProcessDocumentId', 'process_document_id'),
    ),
)

# --------------------------------------------------------------------------
# 6 MOE ModelObjectiveEstimation
# --------------------------------------------------------------------------
MOE = TableSpec(
    code='MOE', name='ModelObjectiveEstimation',
    description='Modelling and objective-estimation applications: how results are encoded, what they are used for, and their quality indicator.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               m.id             AS assessment_method_id,
               m.data_aggregation_process_id,
               m.assessment_method_name,
               m.pollutant_id,
               re.notation      AS result_encoding,
               ma.notation      AS method_application,
               m.generic_mqi,
               m.data_quality_document_id,
               m.method_document_id
        FROM models m
        LEFT JOIN eea_resultencoding   re ON m.result_encoding_id    = re.id
        LEFT JOIN eea_modelapplication ma ON m.method_application_id = ma.id
        ORDER BY m.id, m.data_aggregation_process_id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('DataAggregationProcessId', 'data_aggregation_process_id'),
        Column('AssessmentMethodName', 'assessment_method_name'),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('ResultEncoding', 'result_encoding'),
        Column('MethodApplication', 'method_application'),
        Column('GenericMQI', 'generic_mqi', f.percent),
        Column('DataQualityDocumentId', 'data_quality_document_id'),
        Column('MethodDocumentId', 'method_document_id'),
    ),
)

# --------------------------------------------------------------------------
# 7 OMR ObservationMeasurementResult
# --------------------------------------------------------------------------
OMR = TableSpec(
    code='OMR', name='ObservationMeasurementResult',
    description='Air quality measurement values with their time reference, for the selected reporting year.',
    params=('country_code', 'year'),
    year_dependent=True,
    sql="""
        SELECT %(country_code)s AS country_code,
               sp.id            AS assessment_method_id,
               o.from_time      AS start_time,
               sp.pollutant_id,
               o.to_time        AS end_time,
               o.value,
               co.notation      AS unit,
               o.observationvalidity_id     AS validity,
               o.observationverification_id AS verification,
               o.data_capture,
               tr.notation      AS time_resolution,
               o.touched        AS result_time
        FROM observations o
        JOIN sampling_points sp   ON o.sampling_point_id  = sp.id
        JOIN eea_concentrations co ON sp.unit_id           = co.id
        JOIN eea_times tr          ON sp.time_resolution_id = tr.id
        WHERE o.from_time >= make_timestamp(%(year)s, 1, 1, 0, 0, 0)
          AND o.from_time <  make_timestamp(%(year)s + 1, 1, 1, 0, 0, 0)
        ORDER BY sp.id, o.from_time
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('Start', 'start_time', DATETIME),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('End', 'end_time', DATETIME),
        Column('Value', 'value', f.concentration),
        Column('Unit', 'unit'),
        Column('Validity', 'validity', f.integer),
        Column('Verification', 'verification', f.integer),
        Column('DataCapture', 'data_capture', f.percent),
        Column('TimeResolution', 'time_resolution'),
        Column('ResultTime', 'result_time', DATETIME),
    ),
)

# --------------------------------------------------------------------------
# 8 MRI MOEResultInline
# --------------------------------------------------------------------------
MRI = TableSpec(
    code='MRI', name='MOEResultInline',
    description='Gridded model or objective-estimation results, one row per EPSG:3035 grid cell.',
    params=('country_code', 'year'),
    year_dependent=True,
    sql="""
        SELECT %(country_code)s AS country_code,
               r.assessment_method_id,
               r.start_time,
               r.data_aggregation_process_id,
               r.x,
               r.y,
               r.pollutant_id,
               r.end_time,
               r.value,
               co.notation AS unit,
               r.validity_id AS validity,
               r.spatial_resolution,
               r.result_time
        FROM moe_result_inline r
        LEFT JOIN eea_concentrations co ON r.unit_id = co.id
        WHERE r.start_time >= make_timestamp(%(year)s, 1, 1, 0, 0, 0)
          AND r.start_time <  make_timestamp(%(year)s + 1, 1, 1, 0, 0, 0)
        ORDER BY r.assessment_method_id, r.start_time, r.x, r.y
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('Start', 'start_time', DATETIME),
        Column('DataAggregationProcessId', 'data_aggregation_process_id'),
        Column('X', 'x', f.integer),
        Column('Y', 'y', f.integer),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('End', 'end_time', DATETIME),
        Column('Value', 'value', f.concentration),
        Column('Unit', 'unit'),
        Column('Validity', 'validity', f.integer),
        Column('SpatialResolution', 'spatial_resolution', f.integer),
        Column('ResultTime', 'result_time', DATETIME),
    ),
)

# --------------------------------------------------------------------------
# 9 MRE MOEResultExternal
#
# The guide's example sheet spells MRE_11 "GeoTiffAttchment"; the Attributes
# sheet spells it "GeoTiffAttachment". Following the Attributes sheet.
# --------------------------------------------------------------------------
MRE = TableSpec(
    code='MRE', name='MOEResultExternal',
    description='Gridded model results supplied as an attached GEOTIFF rather than inline grid cells.',
    params=('country_code', 'year'),
    year_dependent=True,
    sql="""
        SELECT %(country_code)s AS country_code,
               r.assessment_method_id,
               r.start_time,
               r.data_aggregation_process_id,
               r.pollutant_id,
               r.end_time,
               co.notation AS unit,
               r.validity_id AS validity,
               r.spatial_resolution,
               r.result_time,
               r.geotiff_attachment
        FROM moe_result_external r
        LEFT JOIN eea_concentrations co ON r.unit_id = co.id
        WHERE r.start_time >= make_timestamp(%(year)s, 1, 1, 0, 0, 0)
          AND r.start_time <  make_timestamp(%(year)s + 1, 1, 1, 0, 0, 0)
        ORDER BY r.assessment_method_id, r.start_time
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('Start', 'start_time', DATETIME),
        Column('DataAggregationProcessId', 'data_aggregation_process_id'),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('End', 'end_time', DATETIME),
        Column('Unit', 'unit'),
        Column('Validity', 'validity', f.integer),
        Column('SpatialResolution', 'spatial_resolution', f.integer),
        Column('ResultTime', 'result_time', DATETIME),
        Column('GeoTiffAttachment', 'geotiff_attachment'),
    ),
)

# --------------------------------------------------------------------------
# 10 ZGE ZoneGeometry
# --------------------------------------------------------------------------
ZGE = TableSpec(
    code='ZGE', name='ZoneGeometry',
    description='Air quality zone boundaries as GeoJSON.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               z.id             AS zone_id,
               ST_AsGeoJSON(ST_Multi(z.geom))::json AS zone_geometry
        FROM zones z
        ORDER BY z.id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('ZoneId', 'zone_id'),
        Column('ZoneGeometryGeoJson', 'zone_geometry', f.geojson_feature),
    ),
)

# --------------------------------------------------------------------------
# 11 ARZ AssessmentRegimeZone
# --------------------------------------------------------------------------
ARZ = TableSpec(
    code='ARZ', name='AssessmentRegimeZone',
    description='Air quality zones and their assessment regimes: objective, target, pollutant, metric, threshold and exemptions.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               ar.id            AS assessment_regime_id,
               ar.zone_id,
               z.zone_national_code,
               z.zone_area,
               zc.notation      AS zone_category,
               zt.notation      AS zone_type,
               z.name           AS zone_name,
               ar.pollutant_id,
               pt.notation      AS protection_target,
               ot.notation      AS objective_type,
               rm.notation      AS reporting_metric,
               ate.notation     AS assessment_threshold_exceedance,
               ar.postponement_year,
               ar.fixed_measurement_reduction,
               ar.zone_resident_population_year,
               ar.zone_resident_population,
               ar.classification_year,
               ar.classification_document_id
        FROM assessment_regimes ar
        LEFT JOIN zones z                              ON ar.zone_id = z.id
        LEFT JOIN eea_zonecategory zc                  ON z.zone_category_id = zc.id
        LEFT JOIN eea_zonetypes zt                     ON z.zone_type_id     = zt.id
        LEFT JOIN eea_protectiontargets pt             ON ar.protection_target_id = pt.id
        LEFT JOIN eea_objectivetypes ot                ON ar.objective_type_id    = ot.id
        LEFT JOIN eea_reportingmetrics rm              ON ar.reporting_metric_id  = rm.id
        LEFT JOIN eea_assessmentthresholdexceedances ate ON ar.assessment_threshold_exceedance_id = ate.id
        ORDER BY ar.id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AssessmentRegimeId', 'assessment_regime_id'),
        Column('ZoneId', 'zone_id'),
        Column('ZoneNationalCode', 'zone_national_code'),
        Column('ZoneArea', 'zone_area', f.concentration),
        Column('ZoneCategory', 'zone_category'),
        Column('ZoneType', 'zone_type'),
        Column('ZoneName', 'zone_name'),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('ProtectionTarget', 'protection_target'),
        Column('ObjectiveType', 'objective_type'),
        Column('ReportingMetric', 'reporting_metric'),
        Column('AssessmentThresholdExceedance', 'assessment_threshold_exceedance'),
        Column('PostponementYear', 'postponement_year', f.integer),
        Column('FixedMeasurementReduction', 'fixed_measurement_reduction', f.boolean),
        Column('ZoneResidentPopulationYear', 'zone_resident_population_year', f.integer),
        Column('ZoneResidentPopulation', 'zone_resident_population', f.integer),
        Column('ClassificationYear', 'classification_year', f.integer),
        Column('ClassificationDocumentId', 'classification_document_id'),
    ),
)

# --------------------------------------------------------------------------
# 12 CAM ComplianceAssessmentMethod
# --------------------------------------------------------------------------
CAM = TableSpec(
    code='CAM', name='ComplianceAssessmentMethod',
    description='Yearly compliance situation per assessment regime and assessment method, with uncertainty and exceedance reason.',
    params=('country_code', 'year'),
    year_dependent=True,
    sql="""
        SELECT %(country_code)s AS country_code,
               c.reporting_year,
               c.assessment_regime_id,
               c.data_aggregation_process_id,
               c.assessment_method_id,
               c.pollutant_id,
               ast.notation AS assessment_type,
               c.is_exceedance,
               c.data_coverage,
               c.pollution_level,
               c.pollution_level_adjusted,
               c.relative_uncertainty_limit,
               c.assessment_mqi,
               c.correction_flag,
               c.attainment_id,
               c.srs_id,
               er.notation AS preliminary_reason,
               c.deletion
        FROM compliance_assessment_method c
        LEFT JOIN eea_assessmenttypes ast  ON c.assessment_type_id    = ast.id
        LEFT JOIN eea_exceedancereason er  ON c.preliminary_reason_id  = er.id
        WHERE c.reporting_year = %(year)s
        ORDER BY c.assessment_regime_id, c.assessment_method_id, c.data_aggregation_process_id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('ReportingYear', 'reporting_year', f.integer),
        Column('AssessmentRegimeId', 'assessment_regime_id'),
        Column('DataAggregationProcessId', 'data_aggregation_process_id'),
        Column('AssessmentMethodId', 'assessment_method_id'),
        Column('PollutantId', 'pollutant_id', f.integer),
        Column('AssessmentType', 'assessment_type'),
        Column('IsExceedance', 'is_exceedance', f.boolean),
        Column('DataCoverage', 'data_coverage', f.percent),
        Column('PollutionLevel', 'pollution_level', f.level),
        Column('PollutionLevelAdjusted', 'pollution_level_adjusted', f.level),
        Column('RelativeUncertaintyLimit', 'relative_uncertainty_limit', f.percent),
        Column('AssessmentMQI', 'assessment_mqi', f.percent),
        Column('CorrectionFlag', 'correction_flag', f.boolean),
        Column('AttainmentId', 'attainment_id'),
        Column('SRSId', 'srs_id'),
        Column('PreliminaryReason', 'preliminary_reason'),
        Column('Deletion', 'deletion', f.boolean),
    ),
)

# --------------------------------------------------------------------------
# 13 SRS SpatialRepresentativeness
# --------------------------------------------------------------------------
SRS = TableSpec(
    code='SRS', name='SpatialRepresentativeness',
    description='Links a spatial representativeness area or exceedance extent to the compliance assessment method.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               sr.id            AS srs_id,
               sr.srs_application_id,
               sa.notation      AS srs_application,
               re.notation      AS result_encoding,
               sr.representativeness_assessment_method_id
        FROM spatial_representativeness sr
        LEFT JOIN eea_srapplication  sa ON sr.srs_application    = sa.id
        LEFT JOIN eea_resultencoding re ON sr.result_encoding_id = re.id
        ORDER BY sr.id, sr.srs_application_id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('SRSId', 'srs_id'),
        Column('SRSApplicationId', 'srs_application_id'),
        Column('SRSApplication', 'srs_application'),
        Column('ResultEncoding', 'result_encoding'),
        Column('RepresentativenessAssessmentMethodId', 'representativeness_assessment_method_id'),
    ),
)

# --------------------------------------------------------------------------
# 14 SRI SRSInline
# --------------------------------------------------------------------------
SRI = TableSpec(
    code='SRI', name='SRSInline',
    description='Representativeness area as a set of EPSG:3035 grid cells.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               sr.srs_application_id,
               i.x,
               i.y,
               i.spatial_resolution
        FROM srs_inline i
        JOIN spatial_representativeness sr ON i.spatial_representativeness_id = sr.id
        ORDER BY sr.srs_application_id, i.x, i.y
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('SRSApplicationId', 'srs_application_id'),
        Column('X', 'x', f.integer),
        Column('Y', 'y', f.integer),
        Column('SpatialResolution', 'spatial_resolution', f.integer),
    ),
)

# --------------------------------------------------------------------------
# 15 SRE SRSExternal
# --------------------------------------------------------------------------
SRE = TableSpec(
    code='SRE', name='SRSExternal',
    description='Representativeness area supplied as an attached GEOTIFF.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               sr.srs_application_id,
               e.spatial_resolution,
               e.geotiff_attachment
        FROM srs_external e
        JOIN spatial_representativeness sr ON e.spatial_representativeness_id = sr.id
        ORDER BY sr.srs_application_id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('SRSApplicationId', 'srs_application_id'),
        Column('SpatialResolution', 'spatial_resolution', f.integer),
        Column('GeoTiffAttachment', 'geotiff_attachment'),
    ),
)

# --------------------------------------------------------------------------
# 16 ADJ PollutionLevelAdjustment
# --------------------------------------------------------------------------
ADJ = TableSpec(
    code='ADJ', name='PollutionLevelAdjustment',
    description='Deductions for natural sources or winter salting and sanding.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               a.attainment_id,
               ast.notation AS adjustment_source,
               a.adjustment_assessment_method_id,
               a.adjustment_document_id
        FROM pollution_level_adjustment a
        LEFT JOIN eea_adjustmentsourcetype ast ON a.adjustment_source_id = ast.id
        ORDER BY a.attainment_id, a.adjustment_source_id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('AttainmentId', 'attainment_id'),
        Column('AdjustmentSource', 'adjustment_source'),
        Column('AdjustmentAssessmentMethodId', 'adjustment_assessment_method_id'),
        Column('AdjustmentDocumentId', 'adjustment_document_id'),
    ),
)

# --------------------------------------------------------------------------
# 22 DOC Documentation
# --------------------------------------------------------------------------
DOC = TableSpec(
    code='DOC', name='Documentation',
    description='Documents referenced from the other tables: data quality reports, model documentation, air quality plans.',
    params=('country_code',),
    sql="""
        SELECT %(country_code)s AS country_code,
               dt.notation   AS data_table,
               dobj.notation AS document_type,
               d.id          AS document_id,
               d.documentattachment AS document_attachment,
               d.document_original_url
        FROM documents d
        LEFT JOIN eea_datatable dt        ON d.datatable_id      = dt.id
        LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
        ORDER BY dt.notation, dobj.notation, d.id
    """,
    columns=(
        Column('CountryCode', 'country_code'),
        Column('DataTable', 'data_table'),
        Column('DocumentType', 'document_type'),
        Column('DocumentId', 'document_id'),
        Column('DocumentAttachment', 'document_attachment'),
        # DOC_05 and DOC_06 are alternatives: a document is either attached to the
        # Reportnet3 envelope or published somewhere and referenced by URL.
        Column('DocumentOriginalURL', 'document_original_url'),
    ),
)


AQR3_TABLES = {t.code: t for t in (
    AUT, STA, SPO, SPL, SPP, MOE, OMR, MRI, MRE, ZGE, ARZ, CAM, SRS, SRI, SRE, ADJ, DOC,
)}

# Legacy slugs from the pre-v5.02 routes, so existing callers keep working.
LEGACY_SLUGS = {
    'authorities': 'AUT',
    'stations': 'STA',
    'samplingpoints': 'SPO',
    'samplingpointlocations': 'SPL',
    'processes': 'SPP',
    'measurements': 'OMR',
    'zonegeometry': 'ZGE',
    'spatialrepresentativeness': 'SRS',
    'srareainline': 'SRI',
}


def resolve(code_or_slug):
    """Look up a table by AQR3 code (preferred) or legacy route slug."""
    key = (code_or_slug or '').strip()
    if key.upper() in AQR3_TABLES:
        return AQR3_TABLES[key.upper()]
    slug = LEGACY_SLUGS.get(key.lower())
    return AQR3_TABLES[slug] if slug else None
