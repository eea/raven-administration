-- ===========================================================================
-- 001 — AQR3 v5.02: SamplingPoint (SPO) + SamplingPointLocation (SPL)
--
-- Aligns sampling_points column names with the AQR3 v5.02 attribute names and
-- adds the SPL location-history table.
--
-- sampling_points and stations stay the authoritative operational store — no
-- columns are moved out of them, so the map view, mean.py, plans_programs_export
-- and both CRUD modules keep working. sampling_point_locations is additive: it
-- only holds per-period overrides, and the SPL export falls back to
-- sampling_points/stations when there is no row.
--
-- Idempotent: safe to re-run.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- 1. Renames (AQR3 attribute -> snake_case)
-- ---------------------------------------------------------------------------

-- sampling_point_ref -> sampling_point_reference_id  (SPO_03)
do
$$
begin
    if exists (select 1
               from information_schema.columns
               where table_name = 'sampling_points'
                 and column_name = 'sampling_point_ref')
        and not exists (select 1
                        from information_schema.columns
                        where table_name = 'sampling_points'
                          and column_name = 'sampling_point_reference_id')
    then
        alter table sampling_points rename column sampling_point_ref to sampling_point_reference_id;
    end if;
end
$$;

-- spo_category_id -> sampling_point_category_id  (SPL_06)
do
$$
begin
    if exists (select 1
               from information_schema.columns
               where table_name = 'sampling_points'
                 and column_name = 'spo_category_id')
        and not exists (select 1
                        from information_schema.columns
                        where table_name = 'sampling_points'
                          and column_name = 'sampling_point_category_id')
    then
        alter table sampling_points rename column spo_category_id to sampling_point_category_id;
    end if;
end
$$;

-- ---------------------------------------------------------------------------
-- 2. New column: Hotspot (SPL_07)
-- ---------------------------------------------------------------------------

alter table sampling_points
    add column if not exists hotspot boolean default false not null;

-- ---------------------------------------------------------------------------
-- 3. Comments
-- ---------------------------------------------------------------------------

comment on table sampling_points is 'v5.0.0 AQR3 v5.02: operational store for a sampling point. Reports as SamplingPoint (SPO) plus the current row of SamplingPointLocation (SPL).';
comment on column sampling_points.id is 'AQR3 SPO_02 AssessmentMethodId';
comment on column sampling_points.sampling_point_reference_id is 'AQR3 SPO_03. Mandatory format: SPOref_<StationEoICode>_<PollutantId>_<idx>';
comment on column sampling_points.pollutant_id is 'AQR3 SPO_04 PollutantId. FK to eea_pollutants.id (numeric)';
comment on column sampling_points.hotspot is 'AQR3 SPL_07. Default location value, overridable per period in sampling_point_locations.';
comment on column sampling_points.sampling_point_category_id is 'AQR3 SPL_06 SamplingPointCategory';
comment on column sampling_points.time_resolution_id is 'AQR3 OMR_11 TimeResolution. FK to eea_times (hour, day, etc.)';
comment on column sampling_points.unit_id is 'AQR3 OMR_07 Unit. FK to eea_concentrations (ug.m-3, etc.)';
comment on column sampling_points.from_time is 'Sampling point active period start. Raven-internal; also the default SPL_03 LocationBegin.';
comment on column sampling_points.logger_id is 'Raven-internal: logger push identifier. No AQR3 equivalent.';
comment on column sampling_points.private is 'Raven-internal: hides the series from non-owning networks. No AQR3 equivalent.';
comment on column sampling_points.use_in_public_api is 'Raven-internal: exposes the series via the public API. No AQR3 equivalent.';
-- daily_check is added and commented by 005_daily_check_log.sql; it does not
-- exist yet at this point, so commenting on it here would abort the migration.

-- ---------------------------------------------------------------------------
-- 4. SamplingPointLocation (SPL)
-- ---------------------------------------------------------------------------

create table if not exists sampling_point_locations
(
    sampling_point_id           varchar(100) not null
        references sampling_points
            on update cascade on delete cascade,
    location_begin              timestamp    not null,
    location_end                timestamp,
    station_area_id             varchar(100)
        references eea_areaclassifications
            on update cascade,
    sampling_point_category_id  varchar(100)
        references eea_spocategory
            on update cascade,
    hotspot                     boolean,
    supersite                   boolean,
    latitude                    numeric(10, 7),
    longitude                   numeric(10, 7),
    altitude                    numeric(6, 1),
    inlet_height                numeric(32, 3),
    building_distance           numeric(32, 3),
    kerb_distance               numeric(32, 3),
    emission_source_distance    numeric(10, 1),
    primary key (sampling_point_id, location_begin),
    constraint sampling_point_locations_period
        check (location_end is null or location_end > location_begin)
);

comment on table sampling_point_locations is 'v5.0.0 AQR3 SPL. Optional per-period location overrides; PK matches the AQR3 key (CountryCode + AssessmentMethodId + LocationBegin). All attribute columns are nullable and fall back to sampling_points/stations.';
comment on column sampling_point_locations.location_begin is 'AQR3 SPL_03';
comment on column sampling_point_locations.location_end is 'AQR3 SPL_04. NULL means still current.';

create index if not exists idx_spl_sp_begin
    on sampling_point_locations (sampling_point_id, location_begin desc);

-- ---------------------------------------------------------------------------
-- 5. Record
--
-- No backfill. An empty sampling_point_locations is the correct starting state:
-- the SPL export falls back to sampling_points/stations with
-- location_begin = sampling_points.from_time, so every sampling point already
-- reports one complete SPL row. Rows are inserted here only when a location
-- actually changes.
-- ---------------------------------------------------------------------------

insert into schema_version (version, description)
values ('5.0.0-spo-spl',
        'AQR3 v5.02: rename sampling_points.sampling_point_ref/spo_category_id, add hotspot, add sampling_point_locations (SPL)')
on conflict (version) do nothing;

commit;
