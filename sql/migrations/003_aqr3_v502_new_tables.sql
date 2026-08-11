-- ===========================================================================
-- 003 — AQR3 v5.02: new tables
--
--   models                        MOE  ModelObjectiveEstimation
--   moe_result_inline             MRI  MOEResultInline        (year-partitioned)
--   moe_result_external           MRE  MOEResultExternal
--   srs_external                  SRE  SRSExternal
--   pollution_level_adjustment    ADJ  PollutionLevelAdjustment
--   compliance_assessment_method  CAM  ComplianceAssessmentMethod
--
-- Idempotent: safe to re-run.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- MOE — ModelObjectiveEstimation
--
-- The model/OBE counterpart of sampling_points: its id is the AssessmentMethodId
-- used by MRI/MRE/CAM/SRS/ADJ when the assessment came from a model rather than a
-- measurement. Mandatory id format is MOD_* or OBE_*.
-- ---------------------------------------------------------------------------

create table if not exists models
(
    id                          varchar(100) not null primary key,
    data_aggregation_process_id varchar(100) not null
        references eea_aggregationprocess
            on update cascade,
    assessment_method_name      varchar(150),
    pollutant_id                integer
        references eea_pollutants
            on update cascade,
    result_encoding_id          varchar(100)
        references eea_resultencoding
            on update cascade,
    method_application_id       varchar(100)
        references eea_modelapplication
            on update cascade,
    generic_mqi                 numeric(5, 2),
    data_quality_document_id    varchar(255)
        references documents
            on update cascade,
    method_document_id          varchar(255)
        references documents
            on update cascade,
    constraint models_id_prefix
        check (id like 'MOD\_%' or id like 'OBE\_%')
);

comment on table models is 'AQR3 MOE ModelObjectiveEstimation. A model or objective-estimation application.';
comment on column models.id is 'AQR3 MOE_02 AssessmentMethodId. Mandatory format: MOD_<specific> or OBE_<specific>.';
comment on column models.data_aggregation_process_id is 'AQR3 MOE_03 DataAggregationProcessId';
comment on column models.assessment_method_name is 'AQR3 MOE_04 AssessmentMethodName';
comment on column models.result_encoding_id is 'AQR3 MOE_06 ResultEncoding — inline (moe_result_inline) or external (moe_result_external)';
comment on column models.method_application_id is 'AQR3 MOE_07 MethodApplication';
comment on column models.generic_mqi is 'AQR3 MOE_08 GenericMQI (modelling quality indicator)';

-- ---------------------------------------------------------------------------
-- MRI — MOEResultInline
--
-- Gridded model results. One row per grid cell per timestep, so this is the
-- highest-volume table in the schema by a wide margin: a national 100 m grid at
-- hourly resolution is billions of rows. Range-partitioned by year, following
-- the observation_log precedent in schema.sql.
-- ---------------------------------------------------------------------------

create table if not exists moe_result_inline
(
    assessment_method_id        varchar(100)  not null,
    start_time                  timestamp     not null,
    data_aggregation_process_id varchar(100)  not null,
    x                           bigint        not null,
    y                           bigint        not null,
    pollutant_id                integer,
    end_time                    timestamp,
    value                       numeric(10, 2),
    unit_id                     varchar(100),
    validity_id                 integer,
    spatial_resolution          integer,
    result_time                 timestamp,
    primary key (assessment_method_id, start_time, data_aggregation_process_id, x, y)
) partition by range (start_time);

comment on table moe_result_inline is 'AQR3 MRI MOEResultInline. Gridded model/OBE results; X/Y are EEA INSPIRE grid coordinates in EPSG:3035, snapped to spatial_resolution. Partitioned by year on start_time.';
comment on column moe_result_inline.x is 'AQR3 MRI_05. EPSG:3035 easting.';
comment on column moe_result_inline.y is 'AQR3 MRI_06. EPSG:3035 northing.';
comment on column moe_result_inline.spatial_resolution is 'AQR3 MRI_12 SpatialResolution in metres (10 | 100 | 1000 | 10000)';

-- No FKs on the partitioned table: a FK from every yearly partition to
-- eea_pollutants/models would add a per-row check on a table sized in the
-- billions. Referential integrity is enforced at the ingest endpoint instead.

create table if not exists moe_result_inline_default
    partition of moe_result_inline default;

do
$$
    declare
        y integer;
    begin
        for y in 2000..2035
            loop
                execute format(
                        'create table if not exists moe_result_inline_%s partition of moe_result_inline for values from (''%s-01-01'') to (''%s-01-01'')',
                        y, y, y + 1);
            end loop;
    end
$$;

create index if not exists idx_mri_method_start
    on moe_result_inline (assessment_method_id, start_time);

-- ---------------------------------------------------------------------------
-- MRE — MOEResultExternal
-- ---------------------------------------------------------------------------

create table if not exists moe_result_external
(
    assessment_method_id        varchar(100) not null
        references models
            on update cascade on delete cascade,
    start_time                  timestamp    not null,
    data_aggregation_process_id varchar(100) not null
        references eea_aggregationprocess
            on update cascade,
    pollutant_id                integer
        references eea_pollutants
            on update cascade,
    end_time                    timestamp,
    unit_id                     varchar(100)
        references eea_concentrations
            on update cascade,
    validity_id                 integer
        references eea_observationvalidity
            on update cascade,
    spatial_resolution          integer,
    result_time                 timestamp,
    geotiff_attachment          varchar(255),
    primary key (assessment_method_id, start_time, data_aggregation_process_id)
);

comment on table moe_result_external is 'AQR3 MRE MOEResultExternal. Gridded model results supplied as an attached GEOTIFF.';
comment on column moe_result_external.geotiff_attachment is 'AQR3 MRE_11 GeoTiffAttchment (sic, spelled GeoTiffAttachment in the Attributes sheet)';

-- ---------------------------------------------------------------------------
-- SRE — SRSExternal
-- ---------------------------------------------------------------------------

create table if not exists srs_external
(
    spatial_representativeness_id varchar(255) not null
        references spatial_representativeness
            on update cascade on delete cascade,
    spatial_resolution            integer,
    geotiff_attachment            varchar(255),
    primary key (spatial_representativeness_id)
);

comment on table srs_external is 'AQR3 SRE. SR area supplied as an attached GEOTIFF instead of inline grid cells.';
comment on column srs_external.geotiff_attachment is 'AQR3 SRE_04 GeoTiffAttachment';

-- ---------------------------------------------------------------------------
-- ADJ — PollutionLevelAdjustment
--
-- Migrated out of exceedancedescriptions, which carried adjustment_source and
-- adjustment_type per exceedance description rather than per attainment.
-- ---------------------------------------------------------------------------

create table if not exists pollution_level_adjustment
(
    attainment_id                   varchar(100) not null,
    adjustment_source_id            varchar(100) not null
        references eea_adjustmentsourcetype
            on update cascade,
    adjustment_assessment_method_id varchar(100),
    adjustment_document_id          varchar(255)
        references documents
            on update cascade,
    primary key (attainment_id, adjustment_source_id)
);

comment on table pollution_level_adjustment is 'AQR3 ADJ. Deductions for natural sources or winter salting/sanding, per attainment situation.';
comment on column pollution_level_adjustment.attainment_id is 'AQR3 ADJ_02 AttainmentId — matches compliance_assessment_method.attainment_id';
comment on column pollution_level_adjustment.adjustment_source_id is 'AQR3 ADJ_03 AdjustmentSource';
comment on column pollution_level_adjustment.adjustment_assessment_method_id is 'AQR3 ADJ_04 — the model/OBE used to quantify the adjustment';

-- Backfill from the existing exceedance descriptions where an adjustment source
-- was recorded. adjustment_type is dropped: AQR3 has no equivalent attribute.
insert into pollution_level_adjustment (attainment_id, adjustment_source_id)
select distinct ed.attainment_id, ed.adjustment_source
from exceedancedescriptions ed
where ed.adjustment_source is not null
on conflict (attainment_id, adjustment_source_id) do nothing;

-- ---------------------------------------------------------------------------
-- CAM — ComplianceAssessmentMethod
--
-- The yearly compliance result per (regime, aggregation, assessment method).
-- Everything here is already computed by core/data/exceedances.py and
-- core/eea/generate_attainment/ but was never persisted, so there was nothing
-- to report. See WP4.
-- ---------------------------------------------------------------------------

create table if not exists compliance_assessment_method
(
    reporting_year              integer      not null,
    assessment_regime_id        varchar(100) not null
        references assessment_regimes
            on update cascade on delete cascade,
    data_aggregation_process_id varchar(100) not null
        references eea_aggregationprocess
            on update cascade,
    assessment_method_id        varchar(100) not null,
    pollutant_id                integer
        references eea_pollutants
            on update cascade,
    assessment_type_id          varchar(100)
        references eea_assessmenttypes
            on update cascade,
    is_exceedance               boolean,
    data_coverage               numeric(5, 2),
    pollution_level             numeric(10, 3),
    pollution_level_adjusted    numeric(10, 3),
    relative_uncertainty_limit  numeric(10, 2),
    assessment_mqi              numeric(5, 2),
    correction_flag             boolean,
    attainment_id               varchar(100),
    srs_id                      varchar(255),
    preliminary_reason_id       varchar(100)
        references eea_exceedancereason
            on update cascade,
    deletion                    boolean default false not null,
    calculated_at               timestamp default CURRENT_TIMESTAMP,
    primary key (reporting_year, assessment_regime_id, data_aggregation_process_id, assessment_method_id)
);

comment on table compliance_assessment_method is 'AQR3 CAM. Persisted yearly compliance results, regenerated by the exceedance/attainment calculation.';
comment on column compliance_assessment_method.assessment_method_id is 'AQR3 CAM_05. Either a sampling_points.id (measurement) or a models.id (model/OBE) — deliberately not a FK, since it spans both.';
comment on column compliance_assessment_method.attainment_id is 'AQR3 CAM_15 AttainmentId. Mandatory format: ATT_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ReportingYear>_<idx>';
comment on column compliance_assessment_method.is_exceedance is 'AQR3 CAM_08 IsExceedance';
comment on column compliance_assessment_method.deletion is 'AQR3 CAM_18 Deletion — flags a previously reported row for withdrawal.';

create index if not exists idx_cam_year
    on compliance_assessment_method (reporting_year);
create index if not exists idx_cam_attainment
    on compliance_assessment_method (attainment_id);

-- ---------------------------------------------------------------------------
-- Done
-- ---------------------------------------------------------------------------

insert into schema_version (version, description)
values ('5.0.0-newtables',
        'AQR3 v5.02: add models (MOE), moe_result_inline (MRI, partitioned), moe_result_external (MRE), srs_external (SRE), pollution_level_adjustment (ADJ), compliance_assessment_method (CAM)')
on conflict (version) do nothing;

commit;
