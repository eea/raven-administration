-- ===========================================================================
-- 002 — AQR3 v5.02: column renames, missing attributes, new vocabularies
--
-- Renames the reporting-specific columns to the snake_case form of their AQR3
-- attribute name.
--
-- NOT renamed, deliberately:
--   * stations.name / networks.name / zones.name — generic column names shared
--     with ~15 unrelated tables. Renaming means disambiguating 240+ `.name`
--     references across users, groups, plugins, notifications and favorites for
--     zero reporting benefit; the export registry aliases them in one line
--     (st.name AS StationName). Same reasoning for PK `id` columns.
--   * observations.from_time / to_time / touched — AQR3 calls them Start / End /
--     ResultTime and `end` is a reserved word. Mapped in the export spec.
--
-- Idempotent: safe to re-run.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- Helper: rename only if the old name is still there and the new one is not
-- ---------------------------------------------------------------------------

create or replace function raven_rename_column(p_table text, p_old text, p_new text)
    returns void
    language plpgsql
as
$$
begin
    if exists (select 1 from information_schema.columns
               where table_name = p_table and column_name = p_old)
        and not exists (select 1 from information_schema.columns
                        where table_name = p_table and column_name = p_new)
    then
        execute format('alter table %I rename column %I to %I', p_table, p_old, p_new);
    end if;
end
$$;

-- ---------------------------------------------------------------------------
-- 1. New vocabulary tables (AQR3 codelists with no table yet)
-- ---------------------------------------------------------------------------

create table if not exists eea_resultencoding
(
    id       varchar(100) not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);
comment on table eea_resultencoding is 'vocabulary/aq/resultencoding (MOE_06, SRS_05)';

create table if not exists eea_modelapplication
(
    id       varchar(100) not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);
comment on table eea_modelapplication is 'vocabulary/aq/modelapplication (MOE_07)';

create table if not exists eea_spatialresolution
(
    id       varchar(100) not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);
comment on table eea_spatialresolution is 'vocabulary/aq/spatialresolution (MRI_12, MRE_09, SRI_05, SRE_03). Metres on the EEA INSPIRE grid: 10 / 100 / 1000 / 10000.';

create table if not exists eea_srapplication
(
    id       varchar(100) not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);
comment on table eea_srapplication is 'vocabulary/aq/SRapplication (SRS_04)';

insert into eea_resultencoding (id, label, notation, uri) values
    ('inline',   'Inline (grid cells in the CSV)', 'inline',   'http://dd.eionet.europa.eu/vocabulary/aq/resultencoding/inline'),
    ('external', 'External (attached GEOTIFF)',    'external', 'http://dd.eionet.europa.eu/vocabulary/aq/resultencoding/external')
on conflict (id) do nothing;

insert into eea_modelapplication (id, label, notation, uri) values
    ('assessment',         'Assessment',                 'assessment',         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/assessment'),
    ('adjustment',         'Adjustment',                 'adjustment',         'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/adjustment'),
    ('scenario',           'Scenario',                   'scenario',           'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/scenario'),
    ('representativeness', 'Spatial representativeness', 'representativeness', 'http://dd.eionet.europa.eu/vocabulary/aq/modelapplication/representativeness')
on conflict (id) do nothing;

insert into eea_spatialresolution (id, label, notation, uri) values
    ('10',    '10 m',    '10',    'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/10'),
    ('100',   '100 m',   '100',   'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/100'),
    ('1000',  '1000 m',  '1000',  'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/1000'),
    ('10000', '10000 m', '10000', 'http://dd.eionet.europa.eu/vocabulary/aq/spatialresolution/10000')
on conflict (id) do nothing;

insert into eea_srapplication (id, label, notation, uri) values
    ('spo_sr', 'Sampling point representativeness area', 'spo_sr', 'http://dd.eionet.europa.eu/vocabulary/aq/SRapplication/spo_sr'),
    ('exc_sr', 'Exceedance extent',                      'exc_sr', 'http://dd.eionet.europa.eu/vocabulary/aq/SRapplication/exc_sr')
on conflict (id) do nothing;

-- AQR3 STA_05: consolidate the v3 eea_organisationallevels rows (a table that
-- never existed in schema.sql) onto eea_administrativelevels.
insert into eea_administrativelevels (id, label, notation, uri) values
    ('international',  'International',   'international',  'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/international'),
    ('local',          'Local',           'local',          'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/local'),
    ('localauthority', 'Local Authority', 'localauthority', 'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/localauthority'),
    ('municipality',   'Municipality',    'municipality',   'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/municipality'),
    ('national',       'National',        'national',       'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/national'),
    ('regional',       'Regional',        'regional',       'http://dd.eionet.europa.eu/vocabulary/aq/administrativelevel/regional')
on conflict (id) do nothing;

-- ---------------------------------------------------------------------------
-- 2. Authority (AUT)
-- ---------------------------------------------------------------------------

select raven_rename_column('authorities', 'organisation_name',    'authority_name');
select raven_rename_column('authorities', 'organisation_url',     'authority_url');
select raven_rename_column('authorities', 'organisation_address', 'authority_address');
select raven_rename_column('authorities', 'instance_id',          'authority_instance_id');
select raven_rename_column('authorities', 'object_id',            'authority_role_id');
select raven_rename_column('authorities', 'status_id',            'authority_status_id');

comment on column authorities.id is 'AQR3 AUT_02 AuthorityInstanceId';
comment on column authorities.authority_role_id is 'AQR3 AUT_03 AuthorityRole -> eea_authorityobject';
comment on column authorities.authority_instance_id is 'AQR3 AUT_05 AuthorityInstance (zone | network | nuts0..3 | station | SPO) -> eea_authorityinstance';

-- ---------------------------------------------------------------------------
-- 3. MeasurementStation (STA)
--
-- STA_09 NetworkDocumentId is the *network's* document denormalised onto the
-- station row, so it belongs on networks. stations.document_id stays as a
-- station-level document (a Raven extension with no AQR3 slot).
-- ---------------------------------------------------------------------------

select raven_rename_column('stations', 'eoi_code',               'station_eoi_code');
select raven_rename_column('stations', 'national_code',          'station_national_code');
select raven_rename_column('stations', 'area_classification_id', 'station_area_id');
select raven_rename_column('networks', 'administration_level_id', 'network_organisational_level_id');

alter table networks
    add column if not exists network_document_id varchar(255)
        references documents on update cascade;

-- STA_06 Timezone. Present in schema.sql from the start but never added by a
-- migration, so the comment below aborted this file on existing databases.
alter table networks
    add column if not exists timezone_id varchar(100)
        references eea_timezones on update cascade;

comment on column stations.station_eoi_code is 'AQR3 STA_02 StationEoICode';
comment on column stations.station_national_code is 'AQR3 STA_07 StationNationalCode';
comment on column stations.station_area_id is 'AQR3 SPL_05 StationArea -> eea_areaclassifications';
comment on column stations.document_id is 'Raven-internal station document. No AQR3 equivalent (STA_09 is the network document, on networks).';
comment on column networks.network_organisational_level_id is 'AQR3 STA_05 NetworkOrganisationalLevel -> eea_administrativelevels';
comment on column networks.network_document_id is 'AQR3 STA_09 NetworkDocumentId';
comment on column networks.timezone_id is 'AQR3 STA_06 Timezone';

-- ---------------------------------------------------------------------------
-- 4. SamplingProcess (SPP)
--
-- activity_begin/end are varchar(25) holding ISO-ish text; AQR3 declares
-- datetime. Cast with a validating USING clause — rows that will not parse
-- abort the migration rather than silently becoming NULL.
-- ---------------------------------------------------------------------------

select raven_rename_column('processes', 'activity_begin', 'process_activity_begin');
select raven_rename_column('processes', 'activity_end',   'process_activity_end');

do
$$
declare
    bad_count integer;
begin
    if exists (select 1 from information_schema.columns
               where table_name = 'processes'
                 and column_name = 'process_activity_begin'
                 and data_type = 'character varying')
    then
        select count(*) into bad_count
        from processes
        where (process_activity_begin is not null
                   and process_activity_begin !~ '^\d{4}-\d{2}-\d{2}')
           or (process_activity_end is not null
                   and process_activity_end !~ '^\d{4}-\d{2}-\d{2}');

        if bad_count > 0 then
            raise exception
                'processes: % row(s) have a non-ISO process_activity_begin/end and cannot be cast to timestamp. Fix them first: SELECT id, process_activity_begin, process_activity_end FROM processes WHERE process_activity_begin !~ ''^\d{4}-\d{2}-\d{2}'' OR process_activity_end !~ ''^\d{4}-\d{2}-\d{2}'';',
                bad_count;
        end if;

        alter table processes
            alter column process_activity_begin type timestamp
                using nullif(process_activity_begin, '')::timestamp,
            alter column process_activity_end type timestamp
                using nullif(process_activity_end, '')::timestamp;
    end if;
end
$$;

-- processes.equipment_identifier is read and written by the processes CRUD
-- (api/endpoints/management/processes/routes.py), core/query.py, the dashboard
-- and latest endpoints, but was only ever created by sql/migrate_airquis.py —
-- so it is missing on any non-NILU install. Same class of gap as the SR tables.
alter table processes
    add column if not exists equipment_identifier varchar(255);

comment on column processes.id is 'AQR3 SPP_02 ProcessId';
comment on column processes.process_activity_begin is 'AQR3 SPP_04';
comment on column processes.process_activity_end is 'AQR3 SPP_05';
comment on column processes.equipment_identifier is 'Raven-internal: serial/asset tag of the physical analyser. No AQR3 equivalent.';

-- ---------------------------------------------------------------------------
-- 5. ObservationMeasurementResult (OMR)
--
-- DataCapture (OMR_10) had no column. ADACS already writes the raw percentage
-- coverage into observations.meta->>'instrument_validity' via RavenDbWriter.cs,
-- which is exactly this quantity, so backfill from there.
-- ---------------------------------------------------------------------------

alter table observations
    add column if not exists data_capture numeric(5, 2);

comment on column observations.data_capture is 'AQR3 OMR_10 DataCapture (percent). Backfilled from meta->>''instrument_validity'' where ADACS supplied it.';

update observations
set data_capture = least(100, greatest(0, (meta ->> 'instrument_validity')::numeric))
where data_capture is null
  and meta ? 'instrument_validity'
  and (meta ->> 'instrument_validity') ~ '^-?\d+(\.\d+)?$'
  and (meta ->> 'instrument_validity')::numeric >= 0;

-- ---------------------------------------------------------------------------
-- 6. ZoneGeometry / AssessmentRegimeZone (ZGE, ARZ)
-- ---------------------------------------------------------------------------

select raven_rename_column('zones', 'code', 'zone_national_code');
select raven_rename_column('zones', 'area', 'zone_area');

comment on column zones.id is 'AQR3 ARZ_03 / ZGE_02 ZoneId';
comment on column zones.zone_national_code is 'AQR3 ARZ_04 ZoneNationalCode';
comment on column zones.zone_area is 'AQR3 ARZ_05 ZoneArea (km2)';

select raven_rename_column('assessment_regimes', 'fixed_spo_reduction',      'fixed_measurement_reduction');
select raven_rename_column('assessment_regimes', 'resident_population',      'zone_resident_population');
select raven_rename_column('assessment_regimes', 'resident_population_year', 'zone_resident_population_year');
select raven_rename_column('assessment_regimes', 'classification_report_id', 'classification_document_id');

alter table assessment_regimes
    add column if not exists postponement_year integer;

comment on column assessment_regimes.id is 'AQR3 ARZ_02 AssessmentRegimeId. Mandatory format: ARE_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ClassificationYear>_<idx>';
comment on column assessment_regimes.postponement_year is 'AQR3 ARZ_14 PostponementYear';
comment on column assessment_regimes.fixed_measurement_reduction is 'AQR3 ARZ_15 FixedMeasurementReduction';
comment on column assessment_regimes.classification_document_id is 'AQR3 ARZ_19 ClassificationDocumentId';

-- ---------------------------------------------------------------------------
-- 7. SpatialRepresentativeness (SRS, SRI)
--
-- These two tables were only ever created by sql/migrate_airquis.py, so the
-- spatialrepresentativeness module and its exports break on a fresh install.
-- Create them here and in schema.sql.
-- ---------------------------------------------------------------------------

create table if not exists spatial_representativeness
(
    id                                   varchar(255) not null primary key,
    srs_application_id                   varchar(255),
    srs_application                       varchar(100),
    representativeness_assessment_method_id varchar(255),
    result_encoding_id                   varchar(100)
        references eea_resultencoding
            on update cascade,
    created_at                           timestamp default CURRENT_TIMESTAMP
);

-- Existing NILU databases have the pre-rename column names.
select raven_rename_column('spatial_representativeness', 'sr_application_id',    'srs_application_id');
select raven_rename_column('spatial_representativeness', 'application',          'srs_application');
select raven_rename_column('spatial_representativeness', 'assessment_method_id', 'representativeness_assessment_method_id');

alter table spatial_representativeness
    add column if not exists result_encoding_id varchar(100)
        references eea_resultencoding on update cascade;

comment on table spatial_representativeness is 'AQR3 SRS. Links an SR area (SPO representativeness or exceedance extent) to the compliance assessment method.';
comment on column spatial_representativeness.id is 'AQR3 SRS_02 SRSId';
comment on column spatial_representativeness.srs_application_id is 'AQR3 SRS_03 SRSApplicationId';
comment on column spatial_representativeness.srs_application is 'AQR3 SRS_04 SRSApplication -> eea_srapplication';
comment on column spatial_representativeness.result_encoding_id is 'AQR3 SRS_05 ResultEncoding -> eea_resultencoding';
comment on column spatial_representativeness.representativeness_assessment_method_id is 'AQR3 SRS_06';

-- sr_area_inline -> srs_inline
do
$$
begin
    if exists (select 1 from information_schema.tables where table_name = 'sr_area_inline')
        and not exists (select 1 from information_schema.tables where table_name = 'srs_inline')
    then
        alter table sr_area_inline rename to srs_inline;
    end if;
end
$$;

create table if not exists srs_inline
(
    id                            serial primary key,
    spatial_representativeness_id varchar(255)
        references spatial_representativeness
            on update cascade on delete cascade,
    x                             bigint,
    y                             bigint,
    spatial_resolution            integer
);

comment on table srs_inline is 'AQR3 SRI. Grid cells of an SR area. X/Y are EEA INSPIRE grid coordinates in EPSG:3035 — see 004 for the reprojection of legacy WGS84 values.';
comment on column srs_inline.x is 'AQR3 SRI_03. EPSG:3035 easting, snapped to spatial_resolution.';
comment on column srs_inline.y is 'AQR3 SRI_04. EPSG:3035 northing, snapped to spatial_resolution.';
comment on column srs_inline.spatial_resolution is 'AQR3 SRI_05 SpatialResolution in metres (10 | 100 | 1000 | 10000)';

-- ---------------------------------------------------------------------------
-- 8. Done
-- ---------------------------------------------------------------------------

drop function if exists raven_rename_column(text, text, text);

insert into schema_version (version, description)
values ('4.502.2',
        'AQR3 v5.02: rename AUT/STA/SPP/ZGE/ARZ/SRS columns, add observations.data_capture, assessment_regimes.postponement_year, networks.network_document_id, 4 new vocabulary tables, SR DDL into core schema')
on conflict (version) do nothing;

commit;
