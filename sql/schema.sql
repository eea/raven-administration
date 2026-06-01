-- =============================================================================
-- RAVEN v4 Database Schema (Reportnet3)
-- Generated from ravendb4 DDL - 2026-04-22
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Custom types
-- ---------------------------------------------------------------------------

DO $$ BEGIN
    CREATE TYPE raven_label_value AS (label text, value text);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE raven_station_timeseries AS (label text, value text, timeseries raven_label_value[]);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- ---------------------------------------------------------------------------
-- EEA vocabulary/lookup tables
-- ---------------------------------------------------------------------------

create table if not exists eea_countries
(
    id       varchar(10)  not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_countries is 'EEA country codes - id is ISO notation';

create table if not exists eea_pollutants
(
    id       integer      not null primary key,
    notation varchar(500) not null,
    label    varchar(500) not null,
    uri      varchar(500) not null unique
);

comment on table eea_pollutants is 'EEA pollutant codes - id is numeric from URI';

create index if not exists idx_pollutants_notation
    on eea_pollutants (notation);

create table if not exists eea_areaclassifications
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_stationclassifications
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_assessmenttypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_concentrations
(
    id       varchar(100) not null primary key,
    notation varchar(100),
    label    varchar(100) not null,
    uri      varchar(255) not null unique
);

create table if not exists eea_times
(
    id       varchar(100)      not null primary key,
    label    varchar(100)      not null,
    notation varchar(100),
    uri      varchar(255)      not null unique,
    timestep integer default 1 not null
);

create table if not exists eea_timezones
(
    id              varchar(100) not null primary key,
    label           varchar(500) not null,
    notation        varchar(100),
    uri             varchar(500) not null unique,
    timezone_offset varchar(10) generated always as (
        CASE
            WHEN ((notation)::text = 'UTC'::text) THEN 'Z'::text
            WHEN ((notation)::text ~~ 'UTC+%'::text)
                THEN (replace((notation)::text, 'UTC'::text, ''::text) || ':00'::text)
            WHEN ((notation)::text ~~ 'UTC-%'::text)
                THEN (replace((notation)::text, 'UTC'::text, ''::text) || ':00'::text)
            ELSE NULL::text
            END) stored
);

comment on column eea_timezones.timezone_offset is 'ISO 8601 offset format (e.g., +02:00, Z) for datetime calculations';

create table if not exists eea_measurementtypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_measurementmethods
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_measurementequipments
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_equivalencedemonstrated
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_analyticaltechnique
(
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_analyticaltechnique is 'Analytical technique vocabulary for Reportnet3';

create table if not exists eea_measurementregimevalues
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_mediavalues
(
    id       varchar(100) not null primary key,
    label    varchar(500) not null,
    notation varchar(100),
    uri      varchar(500) not null unique
);

create table if not exists eea_administrativelevels
(
    id       varchar(100) not null primary key,
    label    varchar(500) not null,
    notation varchar(100),
    uri      varchar(500) not null unique
);

create table if not exists eea_processtypevalues
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_resultnaturevalues
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_zonetypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_zonecategory
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_zonecategory is 'Zone category vocabulary for Reportnet3';

create table if not exists eea_protectiontargets
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_reportingmetrics
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_objecttypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_assessmentthresholdexceedances
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_adjustmenttypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_adjustmentsourcetype
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_exceedancereason
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

create table if not exists eea_exceedancetype
(
    id       integer      not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255)
);

create table if not exists eea_exceedancedescription
(
    id       integer      not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255)
);

create table if not exists eea_aggregationprocess
(
    id       varchar(100) not null primary key,
    label    text         not null,
    notation varchar(100),
    uri      text         not null unique
);

create table if not exists eea_environmentalobjective
(
    id                         integer not null primary key,
    label                      text    not null,
    notation                   varchar(10),
    uri                        text    not null unique,
    definition                 text,
    exceedance_metric          varchar(255),
    objective_type             varchar(255),
    assessment_threshold       varchar(255),
    protection_target          varchar(255),
    reporting_metric           varchar(255),
    aggregation_process        varchar(255),
    exceedance_threshold       numeric(10, 2),
    exceedance_threshold_extra numeric(10, 2),
    related_pollutant          integer
);

comment on table eea_environmentalobjective is 'Environmental objective combinations for assessment regimes (QA rules C10-C19)';

create index if not exists idx_envobj_pollutant
    on eea_environmentalobjective (related_pollutant);

create index if not exists idx_envobj_objective_type
    on eea_environmentalobjective (objective_type);

create table if not exists eea_authorityobject
(
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_authorityobject is 'Authority object/topic vocabulary (e.g., AQD, NEC)';

create table if not exists eea_authorityinstance
(
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_authorityinstance is 'Authority instance level vocabulary (zone, network, nuts, station, SPO)';

create table if not exists eea_authoritystatus
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_authoritystatus is 'Authority status vocabulary (active/inactive)';

create table if not exists eea_spocategory
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_spocategory is 'Sampling point category vocabulary (traffic, background, industrial, etc.)';

create table if not exists eea_objectivetypes
(
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_objectivetypes is 'Assessment objective type vocabulary';

create table if not exists eea_observationvalidity
(
    id       integer      not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_observationvalidity is 'Observation validity flag vocabulary - id is numeric';

create table if not exists eea_observationverification
(
    id       integer      not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_observationverification is 'Observation verification flag vocabulary - id is numeric';

create table if not exists eea_documentobject
(
    id       varchar(50)  not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_documentobject is 'Document object types for AUTH reporting - AQD, Classificationreport, etc.';

create table if not exists eea_datatable
(
    id       varchar(50)  not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

comment on table eea_datatable is 'Data table types - samplingprocess, model, assessmentregimezone, planscenario';

-- ---------------------------------------------------------------------------
-- Settings
-- ---------------------------------------------------------------------------

create table if not exists settings
(
    country_code_id varchar(10)
        references eea_countries
            on update cascade,
    timezone_id     varchar(100)
        references eea_timezones
            on update cascade
);

-- ---------------------------------------------------------------------------
-- Documents
-- ---------------------------------------------------------------------------

create table if not exists documents
(
    id                 varchar(255) not null primary key,
    datatable_id       varchar(50)  not null
        references eea_datatable
            on update cascade,
    documentobject_id  varchar(50)  not null
        references eea_documentobject
            on update cascade,
    documentattachment varchar(500) not null,
    created_at         timestamp default CURRENT_TIMESTAMP
);

comment on table documents is 'v4.8.0 centralized document references for RN3 reporting';

create index if not exists idx_documents_datatable
    on documents (datatable_id);

create index if not exists idx_documents_documentobject
    on documents (documentobject_id);

-- ---------------------------------------------------------------------------
-- Users and groups
-- ---------------------------------------------------------------------------

create table if not exists "group"
(
    id             serial primary key,
    name           varchar(255)          not null unique,
    management     boolean,
    data           boolean,
    exporting      boolean,
    processing     boolean,
    qualitycontrol boolean,
    users          boolean,
    allnetworks    boolean,
    locked         boolean default false not null
);

create table if not exists users
(
    id        serial primary key,
    username  varchar(255)          not null unique,
    password  varchar(255)          not null,
    name      varchar(255),
    created   timestamp,
    createdby varchar(255),
    locked    boolean default false not null
);

create table if not exists usergroup
(
    userid  integer not null
        references users
            on update cascade on delete cascade,
    groupid integer not null
        references "group"
            on update cascade on delete cascade,
    primary key (userid, groupid)
);

-- ---------------------------------------------------------------------------
-- Authorities
-- ---------------------------------------------------------------------------

create table if not exists authorities
(
    id                   varchar(100) not null primary key,
    person_name          varchar(255),
    email                varchar(255) not null,
    organisation_name    varchar(255) not null,
    organisation_url     varchar(255),
    organisation_address varchar(255),
    instance_id          varchar(100)
        references eea_authorityinstance
            on update cascade,
    object_id            varchar(100)
        references eea_authorityobject
            on update cascade,
    status_id            varchar(100)
        references eea_authoritystatus
            on update cascade
);

comment on table authorities is 'Reportnet3 authority contacts - standalone, not linked to specific networks/stations';

-- ---------------------------------------------------------------------------
-- Networks
-- ---------------------------------------------------------------------------

create table if not exists networks
(
    id                      varchar(100) not null primary key,
    name                    varchar(255) not null,
    administration_level_id varchar(100)
        references eea_administrativelevels
            on update cascade,
    timezone_id             varchar(100)
        references eea_timezones
            on update cascade
);

comment on table networks is 'Reportnet3 network table with timezone';

create table if not exists groupnetwork
(
    groupid   integer      not null
        references "group"
            on update cascade on delete cascade,
    networkid varchar(100) not null
        references networks
            on update cascade on delete cascade,
    primary key (groupid, networkid)
);

-- ---------------------------------------------------------------------------
-- Stations
-- ---------------------------------------------------------------------------

create table if not exists stations
(
    id                     varchar(100)   not null primary key,
    eoi_code               varchar(20)    not null,
    name                   varchar(255)   not null,
    national_code          varchar(20),
    latitude               numeric(10, 7) not null,
    longitude              numeric(10, 7) not null,
    altitude               numeric(6, 1),
    supersite              boolean default false,
    area_classification_id varchar(100)
        references eea_areaclassifications
            on update cascade,
    document_id            varchar(255)
        references documents
            on update cascade,
    network_id             varchar(100)   not null
        references networks
            on update cascade on delete cascade
);

comment on table stations is 'v4.8.0 stations with document reference';

-- ---------------------------------------------------------------------------
-- Sampling points
-- ---------------------------------------------------------------------------

create table if not exists sampling_points
(
    id                       varchar(100)          not null primary key,
    sampling_point_ref       varchar(32),
    inlet_height             numeric(32, 3),
    building_distance        numeric(32, 3),
    kerb_distance            numeric(32, 3),
    emission_source_distance numeric(10, 1),
    logger_id                varchar(255),
    private                  boolean default false not null,
    use_in_public_api        boolean default false not null,
    from_time                timestamp,
    to_time                  timestamp,
    pollutant_id             integer               not null
        references eea_pollutants
            on update cascade on delete cascade,
    time_resolution_id       varchar(100)          not null
        references eea_times
            on update cascade on delete cascade,
    unit_id                  varchar(100)          not null
        references eea_concentrations
            on update cascade on delete cascade,
    spo_category_id          varchar(100)
        references eea_spocategory
            on update cascade,
    station_id               varchar(100)          not null
        references stations
            on update cascade on delete cascade,
    daily_check              boolean default false not null
);

comment on table sampling_points is 'v4.4.0 simplified: sample-related data only';
comment on column sampling_points.pollutant_id is 'FK to eea_pollutants.id (numeric)';
comment on column sampling_points.time_resolution_id is 'FK to eea_times (hour, day, etc.)';
comment on column sampling_points.unit_id is 'FK to eea_concentrations (ug.m-3, etc.)';
comment on column sampling_points.daily_check is 'When true, the daily check feature is enabled for this sampling point (shows checkbox in dashboard).';

create index if not exists idx_sp_station_pollutant
    on sampling_points (station_id, pollutant_id);

-- ---------------------------------------------------------------------------
-- Processes
-- ---------------------------------------------------------------------------

create table if not exists processes
(
    id                                    varchar(100) not null primary key,
    activity_begin                        varchar(25)  not null,
    activity_end                          varchar(25),
    measurement_type_id                   varchar(100)
        references eea_measurementtypes
            on update cascade,
    method_id                             varchar(100)
        references eea_measurementmethods
            on update cascade,
    equipment_id                          varchar(100)
        references eea_measurementequipments
            on update cascade,
    analytical_technique_id               varchar(100)
        references eea_analyticaltechnique
            on update cascade,
    equivalence_demonstrated_id           varchar(100)
        references eea_equivalencedemonstrated
            on update cascade,
    sampling_point_id                     varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    data_quality_document_id              varchar(255)
        references documents
            on update cascade,
    equivalence_demonstration_document_id varchar(255)
        references documents
            on update cascade,
    process_document_id                   varchar(255)
        references documents
            on update cascade
);

comment on table processes is 'v4.8.0 simplified: activity times + document reference';

create index if not exists idx_processes_sp
    on processes (sampling_point_id);

-- ---------------------------------------------------------------------------
-- Observations
-- ---------------------------------------------------------------------------

create table if not exists observations
(
    id                         bigserial primary key,
    sampling_point_id          varchar(100)                  not null
        references sampling_points
            on update cascade on delete cascade,
    value                      numeric(255, 5)               not null,
    observationverification_id integer default 3             not null
        references eea_observationverification,
    observationvalidity_id     integer default '-1'::integer not null
        references eea_observationvalidity,
    touched                    timestamp(6)                  not null,
    from_time                  timestamp                     not null,
    to_time                    timestamp                     not null,
    import_value               numeric(255, 5)               not null,
    scaled_value               numeric(255, 5),
    meta                       jsonb,
    constraint un_obs_spoid_fromto
        unique (sampling_point_id, from_time, to_time)
);

comment on table observations is 'v4.6.0: FK to eea_observationvalidity/verification (INTEGER id)';
comment on column observations.observationverification_id is '1=verified, 2=preliminary, 3=not verified';
comment on column observations.observationvalidity_id is '-99=maintenance, -1=not valid, 1=valid, 2=below detection, 3=below+substituted, 4=ozone CCQM';
comment on column observations.import_value is 'Original imported value (before scaling)';
comment on column observations.scaled_value is 'Value after calibration scaling';
comment on column observations.meta is 'NILU instrument metadata: {"instrument_flag": N, "instrument_validity": N.N}. Set by ADACS at import, never modified by QC.';

create index if not exists idx_observations_spid_ft
    on observations (sampling_point_id, from_time);

create index if not exists idx_observations_spid
    on observations (sampling_point_id);

create index if not exists idx_obs_spoid_day
    on observations (sampling_point_id, date_trunc('day'::text, from_time));

create index if not exists idx_obs_spoid_year
    on observations (sampling_point_id, date_trunc('year'::text, from_time));

-- ---------------------------------------------------------------------------
-- Observation change log (partitioned by year)
-- ---------------------------------------------------------------------------

create extension if not exists btree_gist;

create sequence if not exists observation_log_id_seq;

create table if not exists observation_log
(
    id                bigint       not null default nextval('observation_log_id_seq'),
    sampling_point_id varchar(100) not null,
    period            tsrange      not null,
    old_verification  integer,
    new_verification  integer,
    old_validity      integer,
    new_validity      integer,
    old_value         numeric(255, 5),
    new_value         numeric(255, 5),
    old_scaled_value  numeric(255, 5),
    new_scaled_value  numeric(255, 5),
    changed_by        text,
    change_source     text,
    changed_at        timestamp    not null default now(),
    primary key (id, changed_at)
) partition by range (changed_at);

comment on table observation_log is 'Audit log of QC state changes to observations (verification, validity, value, scaled_value), partitioned by year';
comment on column observation_log.period is 'tsrange covering min(from_time)..max(to_time) of all affected observations in the triggering statement';
comment on column observation_log.changed_by is 'JWT username from SET LOCAL app.username; NULL = system/ADACS';
comment on column observation_log.change_source is 'qc_verify | qc_validate | scaling | adacs_import';
comment on column observation_log.old_value is 'Only populated for single-row manual value edits; NULL for bulk operations';
comment on column observation_log.new_value is 'Only populated for single-row manual value edits; NULL for bulk operations';
comment on column observation_log.old_scaled_value is 'Only populated for single-row scaled_value edits; NULL for bulk rescaling';
comment on column observation_log.new_scaled_value is 'Only populated for single-row scaled_value edits; NULL for bulk rescaling';

-- Yearly partitions (2000-2035) + default catch-all for out-of-range data
create table if not exists observation_log_default partition of observation_log default;
do $$
declare
    y integer;
begin
    for y in 2000..2035 loop
        execute format(
            'create table if not exists observation_log_%s partition of observation_log for values from (''%s-01-01'') to (''%s-01-01'')',
            y, y, y + 1
        );
    end loop;
end;
$$;

-- GiST index for range overlap queries: WHERE sampling_point_id = X AND period && tsrange(...)
create index if not exists idx_obs_log_sp_period
    on observation_log using gist (sampling_point_id, period);

-- btree index for timeline queries: WHERE sampling_point_id = X ORDER BY changed_at DESC
create index if not exists idx_obs_log_sp_changed_at
    on observation_log (sampling_point_id, changed_at desc);

-- index for admin/audit queries by source type
create index if not exists idx_obs_log_source
    on observation_log (change_source, changed_at desc);

-- ---------------------------------------------------------------------------
-- Observation change log trigger
-- ---------------------------------------------------------------------------

create or replace function trg_observation_log_fn()
    returns trigger
    language plpgsql
as
$$
declare
    v_username text;
    v_source   text;
begin
    v_username := current_setting('app.username', true);
    v_source   := current_setting('app.change_source', true);

    insert into observation_log (sampling_point_id,
                                 period,
                                 old_verification, new_verification,
                                 old_validity, new_validity,
                                 old_value, new_value,
                                 old_scaled_value, new_scaled_value,
                                 changed_by,
                                 change_source)
    select n.sampling_point_id,
           tsrange(min(n.from_time), max(n.to_time), '[)'),
           -- verification: uniform across bulk QC ops; use max() safely
           case when bool_or(n.observationverification_id is distinct from o.observationverification_id)
                    then max(o.observationverification_id) end,
           case when bool_or(n.observationverification_id is distinct from o.observationverification_id)
                    then max(n.observationverification_id) end,
           -- validity
           case when bool_or(n.observationvalidity_id is distinct from o.observationvalidity_id)
                    then max(o.observationvalidity_id) end,
           case when bool_or(n.observationvalidity_id is distinct from o.observationvalidity_id)
                    then max(n.observationvalidity_id) end,
           -- value: only meaningful for single-row manual edits, NULL for bulk ops
           case when bool_or(n.value is distinct from o.value) and count(*) = 1
                    then max(o.value) end,
           case when bool_or(n.value is distinct from o.value) and count(*) = 1
                    then max(n.value) end,
           -- scaled_value: only meaningful for single-row edits
           case when bool_or(n.scaled_value is distinct from o.scaled_value) and count(*) = 1
                    then max(o.scaled_value) end,
           case when bool_or(n.scaled_value is distinct from o.scaled_value) and count(*) = 1
                    then max(n.scaled_value) end,
           nullif(v_username, ''),
           nullif(v_source, '')
    from new_table n
             join old_table o on n.id = o.id
    where n.observationverification_id is distinct from o.observationverification_id
       or n.observationvalidity_id is distinct from o.observationvalidity_id
       or n.value is distinct from o.value
       or n.scaled_value is distinct from o.scaled_value
    group by n.sampling_point_id;

    return null;
end;
$$;

drop trigger if exists trg_observation_log on observations;
create trigger trg_observation_log
    after update
    on observations
    referencing new table as new_table old table as old_table
    for each statement
execute function trg_observation_log_fn();

-- ---------------------------------------------------------------------------
-- Sampling point log (manual narrative log per sampling point)
-- ---------------------------------------------------------------------------

create table if not exists sampling_point_log
(
    id                bigserial primary key,
    sampling_point_id varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    type              varchar(50)  not null default 'manual',
    comment           text         not null,
    created_at        timestamptz  not null default now(),
    created_date      date         not null default current_date,
    created_by        varchar(250),
    period_from       timestamp    not null,
    period_to         timestamp    not null
);

comment on table sampling_point_log is 'Manual narrative log per sampling point. Equivalent to Oracle AQTL_TIMESERIESLOG.';
comment on column sampling_point_log.type is '''manual'' = management entry, ''daily_check'' = operator daily check, ''migration'' = imported from Oracle';
comment on column sampling_point_log.created_date is 'Calendar date of entry (from created_at, stored explicitly for indexing since timestamptz::date is non-immutable)';
comment on column sampling_point_log.period_from is 'Start of the period this log entry covers (required)';
comment on column sampling_point_log.period_to is 'End of the period this log entry covers (required)';

create index if not exists idx_spl_spid
    on sampling_point_log (sampling_point_id);

create index if not exists idx_spl_spid_created
    on sampling_point_log (sampling_point_id, created_at desc);

create unique index if not exists uq_spl_daily_check_per_day
    on sampling_point_log (sampling_point_id, created_date)
    where type = 'daily_check';

-- ---------------------------------------------------------------------------
-- Scaling, calculated, and converted series
-- ---------------------------------------------------------------------------

create table if not exists scaling_points
(
    id                bigserial primary key,
    sampling_point_id varchar(100)    not null
        references sampling_points
            on update cascade on delete cascade,
    zero_point        numeric(255, 5) not null,
    span_value        numeric(255, 5) not null,
    gas_concentration numeric(255, 5) not null,
    timestamp         timestamp(6)    not null,
    createdby         varchar(255)    not null,
    constraint un_scaling_points_oc_id_timestamp
        unique (sampling_point_id, timestamp)
);

comment on table scaling_points is 'Calibration points for instrument rescaling';

create table if not exists calculated_series
(
    id        bigserial primary key,
    "primary" varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    secondary varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    result    varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    operator  char         not null,
    constraint un_cs_p_s_r
        unique ("primary", secondary, result)
);

comment on table calculated_series is 'Derived measurements from mathematical operations';

create table if not exists converted_series
(
    id                bigserial primary key,
    sampling_point_id varchar(100)    not null unique
        references sampling_points
            on update cascade on delete cascade,
    source            varchar(100)    not null
        references eea_concentrations
            on update cascade on delete cascade,
    target            varchar(100)    not null
        references eea_concentrations
            on update cascade on delete cascade,
    factor            numeric(255, 3) not null,
    createdby         varchar(255)    not null
);

comment on table converted_series is 'Unit conversion factors per sampling point';

-- ---------------------------------------------------------------------------
-- Autovalidated series
-- ---------------------------------------------------------------------------

create table if not exists autovalidated_series
(
    id           serial primary key,
    pollutant_id integer              not null unique
        references eea_pollutants
            on update cascade on delete cascade,
    max          double precision     not null,
    min          double precision     not null,
    rep          integer              not null,
    enabled      boolean default true not null
);

comment on table autovalidated_series is 'QC rules: min/max thresholds and repetition detection';
comment on column autovalidated_series.pollutant_id is 'FK to eea_pollutants.id (numeric)';

-- ---------------------------------------------------------------------------
-- Zones
-- ---------------------------------------------------------------------------

create table if not exists zones
(
    id               varchar(100) not null primary key,
    code             varchar(100) not null,
    name             varchar(254) not null,
    geom             geometry     not null
        constraint enforce_dims_geom
            check (st_ndims(geom) = 2)
        constraint enforce_srid_geom
            check (st_srid(geom) = 4326),
    area             numeric      not null,
    zone_category_id varchar(100)
        references eea_zonecategory
            on update cascade,
    zone_type_id     varchar(100)
        references eea_zonetypes
            on update cascade
);

comment on table zones is 'v4.4.0 simplified zones';

create index if not exists zones_geom_gist
    on zones using gist (geom);

-- ---------------------------------------------------------------------------
-- Assessment regime zones
-- ---------------------------------------------------------------------------

create table if not exists assessmentregime_zones
(
    id                                 serial primary key,
    zone_id                            varchar(100) not null
        references zones
            on update cascade on delete cascade,
    environmental_objective_id         integer      not null
        references eea_environmentalobjective
            on update cascade on delete cascade,
    classification_year                integer      not null,
    document_id                        varchar(255) not null
        references documents
            on update cascade on delete cascade,
    assessment_threshold_exceedance_id varchar(100) not null
        references eea_assessmentthresholdexceedances
            on update cascade,
    constraint assessmentregime_zones_unique
        unique (zone_id, environmental_objective_id, classification_year)
);

comment on table assessmentregime_zones is 'v4.8.0 zone-level assessment regime classification';

create index if not exists idx_assessmentregime_zones_zone_year
    on assessmentregime_zones (zone_id, classification_year);

create index if not exists idx_assessmentregime_zones_env_obj
    on assessmentregime_zones (environmental_objective_id);

-- ---------------------------------------------------------------------------
-- Assessment regimes
-- ---------------------------------------------------------------------------

create table if not exists assessment_regimes
(
    id                                 varchar(100) not null primary key,
    fixed_spo_reduction                boolean default false,
    resident_population_year           integer,
    resident_population                integer,
    classification_year                integer,
    classification_report_id           varchar(255),
    assessment_threshold_exceedance_id varchar(100)
        references eea_assessmentthresholdexceedances
            on update cascade,
    pollutant_id                       integer      not null
        references eea_pollutants
            on update cascade on delete cascade,
    protection_target_id               varchar(100)
        references eea_protectiontargets
            on update cascade,
    objective_type_id                  varchar(100)
        references eea_objectivetypes
            on update cascade,
    reporting_metric_id                varchar(100)
        references eea_reportingmetrics
            on update cascade,
    zone_id                            varchar(100)
        references zones
            on update cascade on delete cascade
);

comment on table assessment_regimes is 'v4.4.0 assessment regimes';
comment on column assessment_regimes.pollutant_id is 'FK to eea_pollutants.id (numeric)';

-- ---------------------------------------------------------------------------
-- Assessment data
-- ---------------------------------------------------------------------------

create table if not exists assessmentdata
(
    id                           varchar(100) not null primary key,
    assessment_regime_id         varchar(100) not null
        references assessment_regimes
            on update cascade on delete cascade,
    assessmentlocal_id           varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    assessmenttype               varchar(100) not null
        references eea_assessmenttypes
            on update cascade on delete cascade,
    assessmentmethodedescription varchar(500)
);

comment on column assessmentdata.assessmentlocal_id is 'Sampling point ID or model ID';

-- ---------------------------------------------------------------------------
-- Attainments
-- ---------------------------------------------------------------------------

create table if not exists attainments
(
    id                   varchar(100) not null primary key,
    name                 varchar(100) not null,
    assessment_regime_id varchar(100) not null
        references assessment_regimes
            on update cascade on delete cascade,
    comment              varchar(500)
);

-- ---------------------------------------------------------------------------
-- Exceedance descriptions
-- ---------------------------------------------------------------------------

create table if not exists exceedancedescriptions
(
    id                            varchar(100) not null primary key,
    attainment_id                 varchar(100) not null
        references attainments
            on update cascade on delete cascade,
    exceedances                   boolean      not null,
    excedance_type                integer      not null
        references eea_exceedancetype,
    max_value                     numeric      not null,
    adjustment_type               varchar(100)
        references eea_adjustmenttypes,
    surface_area                  numeric,
    exposed_population            integer,
    population_reference_year     integer,
    vegetation_area               numeric,
    area_classification           varchar(100)
        references eea_areaclassifications
            on update cascade on delete cascade,
    exceedance_reason             varchar(100)
        references eea_exceedancereason,
    other_exceedance_reason       varchar(500),
    exceedancedescription_element integer      not null
        references eea_exceedancedescription
            on update cascade on delete cascade,
    adjustment_source             varchar(100)
        references eea_adjustmentsourcetype
            on update cascade on delete cascade,
    constraint if_exceed_rea_is_other_then_other_exceed_rea_is_not_null
        check ((NOT ((exceedance_reason)::text = 'other'::text)) OR (other_exceedance_reason IS NOT NULL)),
    constraint if_exceedances_then_area_classification_is_not_null
        check ((NOT exceedances) OR (area_classification IS NOT NULL)),
    constraint if_exceedances_then_exceedance_reason_is_not_null
        check ((NOT exceedances) OR (exceedance_reason IS NOT NULL)),
    constraint if_exceedances_then_exposed_population_is_not_null
        check ((NOT exceedances) OR (exposed_population IS NOT NULL)),
    constraint if_exceedances_then_population_reference_year_is_not_null
        check ((NOT exceedances) OR (population_reference_year IS NOT NULL)),
    constraint if_exceedances_then_adjustment_type_is_not_null
        check ((NOT exceedances) OR (adjustment_type IS NOT NULL)),
    constraint if_exceedances_then_surface_area_is_not_null
        check ((NOT exceedances) OR (surface_area IS NOT NULL))
);

-- ---------------------------------------------------------------------------
-- Exceeding methods
-- ---------------------------------------------------------------------------

create table if not exists exceedingmethods
(
    id                       varchar(100) not null primary key,
    exceedancedescription_id varchar(100) not null
        references exceedancedescriptions
            on update cascade on delete cascade,
    assessmentdata_id        varchar(100) not null
        references assessmentdata
            on update cascade on delete cascade,
    constraint exceedingmethods_unique
        unique (exceedancedescription_id, assessmentdata_id)
);

-- ---------------------------------------------------------------------------
-- Directives
-- ---------------------------------------------------------------------------

create table if not exists directives
(
    pollutant_id    integer not null
        references eea_pollutants
            on update cascade on delete cascade,
    pollutant       text    not null,
    mean_type       integer not null,
    limitvalue_type integer not null,
    valid_from_year integer not null,
    value           numeric,
    count           integer,
    vegetaion_value numeric,
    eco_value       integer,
    reportingmetric text,
    objectivetype   text
);

comment on column directives.pollutant_id is 'FK to eea_pollutants.id (numeric)';

-- ---------------------------------------------------------------------------
-- Statistics
-- ---------------------------------------------------------------------------

create table if not exists statistics
(
    pollutant_id           integer               not null
        references eea_pollutants
            on update cascade on delete cascade,
    aggregation_process_id varchar(100)          not null
        references eea_aggregationprocess
            on update cascade on delete cascade,
    directive_2008_50      boolean default false not null,
    directive_2024_2881    boolean default false not null
);

comment on column statistics.pollutant_id is 'FK to eea_pollutants.id (numeric)';

-- ---------------------------------------------------------------------------
-- Air Quality Index (AQI)
-- ---------------------------------------------------------------------------

create table if not exists aqi
(
    calculation_type text         not null
        constraint aqi_calculation_type_check
            check (calculation_type = ANY (ARRAY ['EEA'::text, 'LOCAL'::text])),
    level            integer      not null,
    description      text         not null,
    color            text         not null,
    range            numrange     not null,
    pollutant_id     integer      not null
        references eea_pollutants
            on update cascade on delete cascade,
    timestep         varchar(100) not null
        references eea_times
            on update cascade on delete cascade,
    primary key (pollutant_id, level, timestep, calculation_type)
);

comment on column aqi.pollutant_id is 'FK to eea_pollutants.id (numeric)';

create index if not exists aqi_range_idx
    on aqi using gist (range);

create index if not exists aqi_pollutant_timestep_idx
    on aqi (pollutant_id, timestep, calculation_type);

-- ---------------------------------------------------------------------------
-- Notifications
-- ---------------------------------------------------------------------------

create table if not exists notifications
(
    name    text                 not null primary key,
    emails  text                 not null,
    enabled boolean default true not null
);

create table if not exists notifications_runs
(
    id                   serial primary key,
    run_timestamp        timestamp with time zone default now() not null,
    missing_data_count   integer                                not null,
    notifications_sent   integer                                not null,
    notifications_failed integer                                not null,
    smtp_server          text,
    execution_time_ms    integer,
    status               text                                   not null,
    error_message        text,
    details              jsonb
);

create index if not exists idx_notifications_runs_timestamp
    on notifications_runs (run_timestamp);

create index if not exists idx_notifications_runs_status
    on notifications_runs (status);

create table if not exists notifications_samplingpoints
(
    notification_id   text         not null
        references notifications
            on update cascade on delete cascade,
    sampling_point_id varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    primary key (sampling_point_id, notification_id)
);

-- ---------------------------------------------------------------------------
-- Schema version tracking
-- ---------------------------------------------------------------------------

create table if not exists schema_version
(
    version     varchar(20) not null primary key,
    description text,
    applied_at  timestamp default CURRENT_TIMESTAMP
);

-- ===========================================================================
-- Functions
-- ===========================================================================

-- Trigger: set touched timestamp on observations insert/update
create or replace function raven_observations_set_timestamp() returns trigger
    language plpgsql
as
$$
BEGIN
    NEW.touched = now();
    RETURN NEW;
END;
$$;

-- Trigger: prevent changes to verified observations
create or replace function raven_observations_check_verification() returns trigger
    language plpgsql
as
$$
BEGIN
    IF OLD.observationverification_id = 1 AND (OLD.value <> NEW.value OR OLD.observationvalidity_id <> NEW.observationvalidity_id)
    THEN
        RAISE EXCEPTION 'Cannot change data when verification flag is set to 1 (verified)';
    END IF;
    RETURN NEW;
END;
$$;

-- Trigger: update sampling_point from_time/to_time on observation insert
create or replace function raven_timeserie_update_time() returns trigger
    language plpgsql
as
$$
DECLARE
    fromtime timestamp without time zone;
    totime   timestamp without time zone;
BEGIN
    SELECT sp.from_time, sp.to_time
    INTO fromtime, totime
    FROM sampling_points sp
    WHERE id = NEW.sampling_point_id;

    IF fromtime IS NULL OR NEW.from_time < fromtime THEN
        UPDATE sampling_points SET from_time = NEW.from_time WHERE id = NEW.sampling_point_id;
    END IF;

    IF totime IS NULL OR NEW.to_time > totime THEN
        UPDATE sampling_points SET to_time = NEW.to_time WHERE id = NEW.sampling_point_id;
    END IF;

    RETURN NEW;
END;
$$;

-- Trigger: limit notification_runs rows to prevent unbounded growth
create or replace function raven_limit_notification_runs() returns trigger
    language plpgsql
as
$$
BEGIN
    DELETE FROM notifications_runs
    WHERE id NOT IN (
        SELECT id FROM notifications_runs
        ORDER BY run_timestamp DESC
        LIMIT 1000
    );
    RETURN NULL;
END;
$$;

-- Scaling function (single calibration point)
create or replace function raven_scale_value(zero double precision, span double precision, gas double precision,
                                             value double precision) returns double precision
    language plpgsql
as
$$
BEGIN
    RETURN ROUND(((gas / (span - zero)) * (value - zero))::numeric, 3);
END;
$$;

-- Scaling function (interpolated between two calibration points)
create or replace function raven_scale_value(prev_zero double precision, prev_span double precision,
                                             prev_gas double precision, prev_timestamp timestamp without time zone,
                                             next_zero double precision, next_span double precision,
                                             next_gas double precision, next_timestamp timestamp without time zone,
                                             value double precision,
                                             value_timestamp timestamp without time zone) returns double precision
    language plpgsql
as
$$
DECLARE
    prev_epoch       DOUBLE PRECISION;
    next_epoch       DOUBLE PRECISION;
    value_epoch      DOUBLE PRECISION;
    zero_diff        DOUBLE PRECISION;
    epoch_diff       DOUBLE PRECISION;
    epoch_value_diff DOUBLE PRECISION;
    span_diff        DOUBLE PRECISION;
    zero             DOUBLE PRECISION;
    span             DOUBLE PRECISION;
BEGIN
    prev_epoch = extract(epoch from prev_timestamp);
    next_epoch = extract(epoch from next_timestamp);
    value_epoch = extract(epoch from value_timestamp);

    zero_diff = next_zero - prev_zero;
    epoch_diff = next_epoch - prev_epoch;
    epoch_value_diff = value_epoch - prev_epoch;
    span_diff = next_span - prev_span;

    zero = prev_zero + (zero_diff / epoch_diff) * epoch_value_diff;
    span = prev_span + (span_diff / epoch_diff) * epoch_value_diff;

    RETURN raven_scale_value(zero, span, prev_gas, value);
END;
$$;

-- ===========================================================================
-- Triggers
-- ===========================================================================

create trigger raven_observations_set_timestamp_trigger
    before insert or update
    on observations
    for each row
execute procedure raven_observations_set_timestamp();

create trigger raven_observations_check_verification_trigger
    before update
    on observations
    for each row
execute procedure raven_observations_check_verification();

create trigger raven_timeserie_update_time_trigger
    after insert
    on observations
    for each row
execute procedure raven_timeserie_update_time();

create trigger limit_notification_runs_trigger
    after insert
    on notifications_runs
    for each row
execute procedure raven_limit_notification_runs();

-- Plugin registry: tracks installed plugins and their configuration
CREATE TABLE IF NOT EXISTS plugin_registry (
    id               VARCHAR PRIMARY KEY,
    name             VARCHAR NOT NULL,
    version          VARCHAR,
    description      TEXT,
    enabled          BOOLEAN NOT NULL DEFAULT TRUE,
    config           JSONB NOT NULL DEFAULT '{}',
    restart_required BOOLEAN NOT NULL DEFAULT FALSE,
    installed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
