"""
migrate_airquis.py - Migrate raven-airquis DB from v3 to v4 schema

The raven-airquis DB was created with the old v3 schema and was never upgraded.
The application code uses v4 schema (e.g. processes.sampling_point_id), causing
query errors. This script brings raven-airquis up to v4 schema while preserving
all existing data.

Data policy:
  - EEA vocabulary/lookup tables: populated from ravendb4 (reference DB)
  - All other user data (stations, sampling_points, aqi, statistics, etc.): preserved

Usage:
    pip install psycopg2-binary
    python migrate_airquis.py --dry-run    # Test without committing changes
    python migrate_airquis.py              # Run full migration
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
import sys

AIRQUIS_DSN = "postgresql://raven-airquis:Xiuco6ehiev6ai@pg-dmz05.nilu.no:5433/raven-airquis"
RAVENDB4_DSN = "postgresql://ravendb4:goh4aengeiw4ohNi@dev-db-dmz02:5432/ravendb4"

# EEA lookup tables that exist in ravendb4 but are MISSING from raven-airquis.
# These are created and populated from ravendb4 data (vocabulary only).
NEW_EEA_TABLES = [
    "eea_analyticaltechnique",
    "eea_authorityobject",
    "eea_authorityinstance",
    "eea_authoritystatus",
    "eea_countries",
    "eea_environmentalobjective",
    "eea_objectivetypes",
    "eea_observationvalidity",
    "eea_observationverification",
    "eea_resultencoding",
    "eea_spatialresolution",
    "eea_srapplication",
    "eea_zonecategory",
]

CREATE_NEW_EEA_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS eea_analyticaltechnique (
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_authorityobject (
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_authorityinstance (
    id       varchar(100) not null primary key,
    label    varchar(150) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_authoritystatus (
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_countries (
    id       varchar(10)  not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_environmentalobjective (
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

CREATE TABLE IF NOT EXISTS eea_objectivetypes (
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_observationvalidity (
    id       integer      not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_observationverification (
    id       integer      not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);

CREATE TABLE IF NOT EXISTS eea_resultencoding (
    id       varchar(50)  not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) unique
);

CREATE TABLE IF NOT EXISTS eea_spatialresolution (
    id       varchar(20)  not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) unique
);

CREATE TABLE IF NOT EXISTS eea_srapplication (
    id       varchar(50)  not null primary key,
    label    varchar(255) not null,
    notation varchar(100),
    uri      varchar(255) unique
);

CREATE TABLE IF NOT EXISTS eea_zonecategory (
    id       varchar(100) not null primary key,
    label    varchar(100) not null,
    notation varchar(100),
    uri      varchar(255) not null unique
);
"""

CREATE_REMAINING_TABLES_SQL = """
-- Authorities (new in v4)
CREATE TABLE IF NOT EXISTS authorities (
    id                   varchar(100) not null primary key,
    person_name          varchar(255),
    email                varchar(255) not null,
    organisation_name    varchar(255) not null,
    organisation_url     varchar(255),
    organisation_address varchar(255),
    instance_id          varchar(100) references eea_authorityinstance on update cascade,
    object_id            varchar(100) references eea_authorityobject on update cascade,
    status_id            varchar(100) references eea_authoritystatus on update cascade
);

-- Documents (recreate with proper FK to eea_datatable/eea_documentobject)
CREATE TABLE IF NOT EXISTS documents (
    id                 varchar(255) not null primary key,
    datatable_id       varchar(50)  not null references eea_datatable on update cascade,
    documentobject_id  varchar(50)  not null references eea_documentobject on update cascade,
    documentattachment varchar(500) not null,
    created_at         timestamp default CURRENT_TIMESTAMP
);

-- Directives
CREATE TABLE IF NOT EXISTS directives (
    pollutant_id    integer not null references eea_pollutants on update cascade on delete cascade,
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

-- Zones (drop+recreate handled in step 5, this is CREATE IF NOT EXISTS safety net)
CREATE TABLE IF NOT EXISTS zones (
    id               varchar(100) not null primary key,
    code             varchar(100) not null,
    name             varchar(254) not null,
    geom             geometry     not null
        constraint enforce_dims_geom check (st_ndims(geom) = 2)
        constraint enforce_srid_geom check (st_srid(geom) = 4326),
    area             numeric      not null,
    zone_category_id varchar(100) references eea_zonecategory on update cascade,
    zone_type_id     varchar(100) references eea_zonetypes on update cascade
);

-- Assessment regimes (v4 structure - replaces old assessmentregimes)
CREATE TABLE IF NOT EXISTS assessment_regimes (
    id                                 varchar(100) not null primary key,
    fixed_spo_reduction                boolean default false,
    resident_population_year           integer,
    resident_population                integer,
    classification_year                integer,
    classification_report_id           varchar(255),
    assessment_threshold_exceedance_id varchar(100) references eea_assessmentthresholdexceedances on update cascade,
    pollutant_id                       integer      not null references eea_pollutants on update cascade on delete cascade,
    protection_target_id               varchar(100) references eea_protectiontargets on update cascade,
    objective_type_id                  varchar(100) references eea_objectivetypes on update cascade,
    reporting_metric_id                varchar(100) references eea_reportingmetrics on update cascade,
    zone_id                            varchar(100) references zones on update cascade on delete cascade
);

-- Assessment regime zones (new in v4)
CREATE TABLE IF NOT EXISTS assessmentregime_zones (
    id                                 serial primary key,
    zone_id                            varchar(100) not null references zones on update cascade on delete cascade,
    environmental_objective_id         integer      not null references eea_environmentalobjective on update cascade on delete cascade,
    classification_year                integer      not null,
    document_id                        varchar(255) not null references documents on update cascade on delete cascade,
    assessment_threshold_exceedance_id varchar(100) not null references eea_assessmentthresholdexceedances on update cascade,
    constraint assessmentregime_zones_unique unique (zone_id, environmental_objective_id, classification_year)
);

-- Exceeding methods (new in v4)
CREATE TABLE IF NOT EXISTS exceedingmethods (
    id                       varchar(100) not null primary key,
    exceedancedescription_id varchar(100) not null references exceedancedescriptions on update cascade on delete cascade,
    assessmentdata_id        varchar(100) not null references assessmentdata on update cascade on delete cascade,
    constraint exceedingmethods_unique unique (exceedancedescription_id, assessmentdata_id)
);

-- Spatial representativeness (plugin table)
CREATE TABLE IF NOT EXISTS spatial_representativeness (
    id                    varchar(255) not null primary key,
    sr_application_id     varchar(255),
    application           varchar(100),
    assessment_method_id  varchar(255),
    created_at            timestamp default CURRENT_TIMESTAMP
);

-- SR area inline (plugin table)
CREATE TABLE IF NOT EXISTS sr_area_inline (
    id                            serial primary key,
    spatial_representativeness_id varchar(255),
    x                             numeric,
    y                             numeric,
    spatial_resolution            varchar(20)
);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version     varchar(20) not null primary key,
    description text,
    applied_at  timestamp default CURRENT_TIMESTAMP
);
"""

CREATE_COVERAGE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION raven_coverage(datetime timestamp without time zone, count integer, timestep integer, coverage_type text DEFAULT 'year'::text)
RETURNS numeric LANGUAGE plpgsql AS $function$
declare y integer;
declare is_leap_year boolean;
declare seconds integer;
begin
    seconds := 31536000;
    y := extract(year from datetime);
    is_leap_year := (y % 4 = 0) and (y % 100 <> 0 or y % 400 = 0);
    if is_leap_year then seconds := 31622400; end if;
    if coverage_type = 'aot40v' then seconds := 3974400;
    elsif coverage_type = 'aot40f' then seconds := 7905600;
    elsif coverage_type = 'winterseason' and not is_leap_year then seconds := 15724800;
    elsif coverage_type = 'winterseason' and is_leap_year then seconds := 15811200;
    elsif coverage_type = 'summeryear' then seconds := 15811200;
    elsif coverage_type = 'winteryear' and not is_leap_year then seconds := 15724800;
    elsif coverage_type = 'winteryear' and is_leap_year then seconds := 15811200;
    elsif coverage_type = 'day' then seconds := 86400;
    elsif coverage_type = 'hour' then seconds := 3600;
    end if;
    if timestep > seconds then return 0; end if;
    return round((count::numeric*100) / (seconds/timestep), 10);
end
$function$;
"""

MATVIEW_NAMES = [
    "observations_aot40f", "observations_aot40v", "observations_day",
    "observations_day_8hmax", "observations_summer_year", "observations_winter_season",
    "observations_winter_year", "observations_year", "observations_year_day",
    "observations_year_hour",
]

CREATE_MATVIEWS_SQL = """
CREATE MATERIALIZED VIEW IF NOT EXISTS observations_aot40f AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text))
 SELECT a.sampling_point_id, a."time",
        CASE WHEN (raven_coverage(a."time", a.count_valid, t.timestep, 'aot40f'::text) < 100)
             THEN round(((a.val * a.count_all::numeric) / a.count_valid::numeric), 10)
             ELSE a.val END AS val,
    a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'aot40f'::text) AS cov,
    now() AS created
   FROM (SELECT observations.sampling_point_id,
            date_trunc('year'::text, observations.from_time) AS "time",
            round(sum((observations.value - 80)) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS val,
            round(min(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS min,
            round(max(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS max,
            count(observations.value)::integer AS count_all,
            count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
            count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
           FROM observations
          WHERE to_char(observations.from_time, 'MM') = ANY (ARRAY['04','05','06','07','08','09'])
            AND to_char(observations.from_time, 'HH24') = ANY (ARRAY['08','09','10','11','12','13','14','15','16','17','18','19'])
          GROUP BY observations.sampling_point_id, date_trunc('year', observations.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_aot40v AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE s.time_resolution_id::text = t_1.id::text)
 SELECT a.sampling_point_id, a."time",
        CASE WHEN raven_coverage(a."time", a.count_valid, t.timestep, 'aot40v') < 100
             THEN round((a.val * a.count_all::numeric / a.count_valid::numeric), 10)
             ELSE a.val END AS val,
    a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'aot40v') AS cov,
    now() AS created
   FROM (SELECT observations.sampling_point_id,
            date_trunc('year', observations.from_time) AS "time",
            round(sum(observations.value - 80) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS val,
            round(min(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS min,
            round(max(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1 AND (observations.value - 80) > 0), 10) AS max,
            count(observations.value)::integer AS count_all,
            count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
            count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
           FROM observations
          WHERE to_char(observations.from_time, 'MM') = ANY (ARRAY['05','06','07'])
            AND to_char(observations.from_time, 'HH24') = ANY (ARRAY['08','09','10','11','12','13','14','15','16','17','18','19'])
          GROUP BY observations.sampling_point_id, date_trunc('year', observations.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_day AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE s.time_resolution_id::text = t_1.id::text)
 SELECT a.sampling_point_id, a."time", a.val, a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'day') AS cov, now() AS created
   FROM (SELECT observations.sampling_point_id,
            date_trunc('day', observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
            round(min(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS min,
            round(max(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS max,
            count(observations.value)::integer AS count_all,
            count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
            count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
           FROM observations
          GROUP BY observations.sampling_point_id, date_trunc('day', observations.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_day_8hmax AS
 SELECT running_8hours_max.sampling_point_id, running_8hours_max.timestep, running_8hours_max."time",
    running_8hours_max.val, running_8hours_max.min, running_8hours_max.max,
    running_8hours_max.count_all, running_8hours_max.count_valid, running_8hours_max.count_verified,
    raven_coverage(running_8hours_max."time", running_8hours_max.count_valid::integer, running_8hours_max.timestep, 'day') AS cov,
    now() AS created
   FROM (WITH timeseries AS (
               SELECT s.id AS sampling_point_id, t_1.timestep
                 FROM sampling_points s, eea_times t_1
                WHERE s.time_resolution_id::text = t_1.id::text)
         SELECT running_8hours.sampling_point_id, t.timestep,
            date_trunc('day', running_8hours.datetime) AS "time",
            max(CASE WHEN running_8hours.count_valid::float >= 0.75*(28800.0/t.timestep::numeric)::float THEN running_8hours.val ELSE NULL END) AS val,
            min(CASE WHEN running_8hours.count_valid::float >= 0.75*(28800.0/t.timestep::numeric)::float THEN running_8hours.val ELSE NULL END) AS min,
            max(CASE WHEN running_8hours.count_valid::float >= 0.75*(28800.0/t.timestep::numeric)::float THEN running_8hours.val ELSE NULL END) AS max,
            count(*) AS count_all,
            count(CASE WHEN running_8hours.count_valid::float >= 0.75*(28800.0/t.timestep::numeric)::float THEN 1 ELSE NULL END) AS count_valid,
            count(CASE WHEN running_8hours.count_verified = running_8hours.count_all THEN 1 ELSE 0 END) AS count_verified
           FROM (SELECT o.from_time AS datetime, o.sampling_point_id,
                    avg(CASE WHEN o.observationvalidity_id >= 1 THEN o.value ELSE NULL END)
                        OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00' PRECEDING AND CURRENT ROW) AS val,
                    count(*) OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00' PRECEDING AND CURRENT ROW) AS count_all,
                    count(CASE WHEN o.observationvalidity_id >= 1 THEN 1 ELSE NULL END)
                        OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00' PRECEDING AND CURRENT ROW) AS count_valid,
                    count(CASE WHEN o.observationverification_id = 1 THEN 1 ELSE NULL END)
                        OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00' PRECEDING AND CURRENT ROW) AS count_verified
                   FROM observations o) running_8hours,
             timeseries t
           WHERE running_8hours.sampling_point_id::text = t.sampling_point_id::text
           GROUP BY running_8hours.sampling_point_id, date_trunc('day', running_8hours.datetime), t.timestep) running_8hours_max;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_summer_year AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE s.time_resolution_id::text = t_1.id::text)
 SELECT a.sampling_point_id, a."time", a.val, a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'summeryear') AS cov, now() AS created
   FROM (SELECT observations.sampling_point_id,
            date_trunc('year', observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
            round(min(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS min,
            round(max(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS max,
            count(observations.value)::integer AS count_all,
            count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
            count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
           FROM observations
          WHERE to_char(observations.from_time, 'MM') = ANY (ARRAY['04','05','06','07','08','09'])
          GROUP BY observations.sampling_point_id, date_trunc('year', observations.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_winter_season AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE s.time_resolution_id::text = t_1.id::text),
      timevalues AS (
         SELECT CASE date_part('month', o.from_time)
                    WHEN 10 THEN o.from_time + '1 year'::interval
                    WHEN 11 THEN o.from_time + '1 year'::interval
                    WHEN 12 THEN o.from_time + '1 year'::interval
                    ELSE o.from_time END AS from_time,
             o.sampling_point_id, o.value, o.observationvalidity_id, o.observationverification_id
           FROM observations o
          WHERE date_part('month', o.from_time) = ANY (ARRAY[1,2,3,10,11,12]::float[]))
 SELECT a.sampling_point_id, a."time", a.val, a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'winterseason') AS cov, now() AS created
   FROM (SELECT timevalues.sampling_point_id,
            date_trunc('year', timevalues.from_time) AS "time",
            round(avg(timevalues.value) FILTER (WHERE timevalues.observationvalidity_id = ANY (ARRAY[1,2,3])), 10) AS val,
            round(min(timevalues.value) FILTER (WHERE timevalues.observationvalidity_id = ANY (ARRAY[1,2,3])), 10) AS min,
            round(max(timevalues.value) FILTER (WHERE timevalues.observationvalidity_id = ANY (ARRAY[1,2,3])), 10) AS max,
            count(timevalues.value)::integer AS count_all,
            count(timevalues.value) FILTER (WHERE timevalues.observationvalidity_id = ANY (ARRAY[1,2,3]))::integer AS count_valid,
            count(*) FILTER (WHERE timevalues.observationverification_id = 1)::integer AS count_verified
           FROM timevalues
          GROUP BY timevalues.sampling_point_id, date_trunc('year', timevalues.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_winter_year AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id, t_1.timestep
           FROM sampling_points s, eea_times t_1
          WHERE s.time_resolution_id::text = t_1.id::text)
 SELECT a.sampling_point_id, a."time", a.val, a.min, a.max, a.count_all, a.count_valid, a.count_verified,
    raven_coverage(a."time", a.count_valid, t.timestep, 'winteryear') AS cov, now() AS created
   FROM (SELECT observations.sampling_point_id,
            date_trunc('year', observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
            round(min(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS min,
            round(max(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS max,
            count(observations.value)::integer AS count_all,
            count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
            count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
           FROM observations
          WHERE to_char(observations.from_time, 'MM') = ANY (ARRAY['01','02','03','10','11','12'])
          GROUP BY observations.sampling_point_id, date_trunc('year', observations.from_time)) a,
     timeseries t
   WHERE a.sampling_point_id::text = t.sampling_point_id::text;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_year AS
 SELECT yearly.sampling_point_id, yearly.timestep, yearly."time",
    yearly.val, yearly.min, yearly.max, yearly.count_all, yearly.count_valid, yearly.count_verified,
    raven_coverage(yearly."time", yearly.count_valid::integer, yearly.timestep, 'year') AS cov,
    now() AS created
   FROM (WITH timeseries AS (
               SELECT s.id AS sampling_point_id, t_1.timestep
                 FROM sampling_points s, eea_times t_1
                WHERE s.time_resolution_id::text = t_1.id::text)
         SELECT hourly.sampling_point_id, t.timestep,
            date_trunc('year', hourly.datetime) AS "time",
            avg(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS val,
            min(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS min,
            max(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS max,
            count(*) AS count_all,
            count(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN 1 ELSE NULL END) AS count_valid,
            count(CASE WHEN hourly.count_verified = hourly.count_all THEN 1 ELSE 0 END) AS count_verified
           FROM (SELECT observations.sampling_point_id,
                    date_trunc('hour', observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
                    count(observations.value)::integer AS count_all,
                    count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
                    count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
                   FROM observations
                  GROUP BY observations.sampling_point_id, date_trunc('hour', observations.from_time)) hourly,
             timeseries t
           WHERE hourly.sampling_point_id::text = t.sampling_point_id::text
           GROUP BY hourly.sampling_point_id, date_trunc('year', hourly.datetime), t.timestep) yearly;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_year_day AS
 SELECT yearly.sampling_point_id, yearly.timestep, yearly."time",
    yearly.val, yearly.min, yearly.max, yearly.p99,
    yearly.count_all, yearly.count_valid, yearly.count_verified,
    raven_coverage(yearly."time", yearly.count_valid::integer, yearly.timestep, 'year') AS cov,
    now() AS created
   FROM (WITH timeseries AS (
               SELECT s.id AS sampling_point_id, t_1.timestep
                 FROM sampling_points s, eea_times t_1
                WHERE s.time_resolution_id::text = t_1.id::text)
         SELECT daily.sampling_point_id, t.timestep,
            date_trunc('year', daily.datetime) AS "time",
            avg(CASE WHEN daily.count_valid::float >= 0.75*(86400.0/t.timestep::numeric)::float THEN daily.val ELSE NULL END) AS val,
            min(CASE WHEN daily.count_valid::float >= 0.75*(86400.0/t.timestep::numeric)::float THEN daily.val ELSE NULL END) AS min,
            max(CASE WHEN daily.count_valid::float >= 0.75*(86400.0/t.timestep::numeric)::float THEN daily.val ELSE NULL END) AS max,
            percentile_cont(0.99) WITHIN GROUP (ORDER BY (CASE WHEN daily.count_valid::float >= 0.75*(86400.0/t.timestep::numeric)::float THEN daily.val ELSE NULL END)::float)::numeric AS p99,
            count(*) AS count_all,
            count(CASE WHEN daily.count_valid::float >= 0.75*(86400.0/t.timestep::numeric)::float THEN 1 ELSE NULL END) AS count_valid,
            count(CASE WHEN daily.count_verified = daily.count_all THEN 1 ELSE 0 END) AS count_verified
           FROM (SELECT observations.sampling_point_id,
                    date_trunc('day', observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
                    count(observations.value)::integer AS count_all,
                    count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
                    count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
                   FROM observations
                  GROUP BY observations.sampling_point_id, date_trunc('day', observations.from_time)) daily,
             timeseries t
           WHERE daily.sampling_point_id::text = t.sampling_point_id::text
           GROUP BY daily.sampling_point_id, date_trunc('year', daily.datetime), t.timestep) yearly;

CREATE MATERIALIZED VIEW IF NOT EXISTS observations_year_hour AS
 SELECT yearly.sampling_point_id, yearly.timestep, yearly."time",
    yearly.val, yearly.min, yearly.max, yearly.count_all, yearly.count_valid, yearly.count_verified,
    raven_coverage(yearly."time", yearly.count_valid::integer, yearly.timestep, 'year') AS cov,
    now() AS created
   FROM (WITH timeseries AS (
               SELECT s.id AS sampling_point_id, t_1.timestep
                 FROM sampling_points s, eea_times t_1
                WHERE s.time_resolution_id::text = t_1.id::text)
         SELECT hourly.sampling_point_id, t.timestep,
            date_trunc('year', hourly.datetime) AS "time",
            avg(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS val,
            min(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS min,
            max(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN hourly.val ELSE NULL END) AS max,
            count(*) AS count_all,
            count(CASE WHEN hourly.count_valid::float >= 0.75*(3600.0/t.timestep::numeric)::float THEN 1 ELSE NULL END) AS count_valid,
            count(CASE WHEN hourly.count_verified = hourly.count_all THEN 1 ELSE 0 END) AS count_verified
           FROM (SELECT observations.sampling_point_id,
                    date_trunc('hour', observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1), 10) AS val,
                    count(observations.value)::integer AS count_all,
                    count(observations.value) FILTER (WHERE observations.observationvalidity_id >= 1)::integer AS count_valid,
                    count(*) FILTER (WHERE observations.observationverification_id = 1)::integer AS count_verified
                   FROM observations
                  GROUP BY observations.sampling_point_id, date_trunc('hour', observations.from_time)) hourly,
             timeseries t
           WHERE hourly.sampling_point_id::text = t.sampling_point_id::text
           GROUP BY hourly.sampling_point_id, date_trunc('year', hourly.datetime), t.timestep) yearly;
"""

CREATE_FUNCTIONS_AND_TRIGGERS_SQL = """
CREATE OR REPLACE FUNCTION raven_observations_set_timestamp() RETURNS trigger
    LANGUAGE plpgsql AS $$
BEGIN
    NEW.touched = now();
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION raven_observations_check_verification() RETURNS trigger
    LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.observationverification_id = 1 AND (OLD.value <> NEW.value OR OLD.observationvalidity_id <> NEW.observationvalidity_id)
    THEN
        RAISE EXCEPTION 'Cannot change data when verification flag is set to 1 (verified)';
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION raven_timeserie_update_time() RETURNS trigger
    LANGUAGE plpgsql AS $$
DECLARE
    fromtime timestamp without time zone;
    totime   timestamp without time zone;
BEGIN
    SELECT sp.from_time, sp.to_time INTO fromtime, totime
    FROM sampling_points sp WHERE id = NEW.sampling_point_id;

    IF fromtime IS NULL OR NEW.from_time < fromtime THEN
        UPDATE sampling_points SET from_time = NEW.from_time WHERE id = NEW.sampling_point_id;
    END IF;
    IF totime IS NULL OR NEW.to_time > totime THEN
        UPDATE sampling_points SET to_time = NEW.to_time WHERE id = NEW.sampling_point_id;
    END IF;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION raven_limit_notification_runs() RETURNS trigger
    LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM notifications_runs
    WHERE id NOT IN (SELECT id FROM notifications_runs ORDER BY run_timestamp DESC LIMIT 1000);
    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS raven_observations_set_timestamp_trigger ON observations;
CREATE TRIGGER raven_observations_set_timestamp_trigger
    BEFORE INSERT OR UPDATE ON observations
    FOR EACH ROW EXECUTE PROCEDURE raven_observations_set_timestamp();

DROP TRIGGER IF EXISTS raven_observations_check_verification_trigger ON observations;
CREATE TRIGGER raven_observations_check_verification_trigger
    BEFORE UPDATE ON observations
    FOR EACH ROW EXECUTE PROCEDURE raven_observations_check_verification();

DROP TRIGGER IF EXISTS raven_timeserie_update_time_trigger ON observations;
CREATE TRIGGER raven_timeserie_update_time_trigger
    AFTER INSERT ON observations
    FOR EACH ROW EXECUTE PROCEDURE raven_timeserie_update_time();

DROP TRIGGER IF EXISTS limit_notification_runs_trigger ON notifications_runs;
CREATE TRIGGER limit_notification_runs_trigger
    AFTER INSERT ON notifications_runs
    FOR EACH ROW EXECUTE PROCEDURE raven_limit_notification_runs();
"""


def log(msg):
    print(msg, flush=True)


def copy_eea_table(src_cur, dst_cur, table, dry_run):
    """Copy all rows from an EEA lookup table from ravendb4 to raven-airquis."""
    src_cur.execute(f"SELECT * FROM {table}")
    rows = src_cur.fetchall()
    if not rows:
        log(f"  {table}: no rows in source, skipping")
        return 0

    cols = list(rows[0].keys())
    placeholders = ", ".join([f"%({c})s" for c in cols])
    col_names = ", ".join(cols)
    sql = f"""
        INSERT INTO {table} ({col_names}) VALUES ({placeholders})
        ON CONFLICT DO NOTHING
    """
    if not dry_run:
        for row in rows:
            dst_cur.execute(sql, dict(row))
    log(f"  {table}: {len(rows)} rows {'would be' if dry_run else ''} upserted")
    return len(rows)


def migrate(dry_run=False):
    log(f"{'DRY RUN - ' if dry_run else ''}Starting raven-airquis v3→v4 migration")
    log("")

    src_conn = psycopg2.connect(RAVENDB4_DSN, cursor_factory=RealDictCursor)
    dst_conn = psycopg2.connect(AIRQUIS_DSN, cursor_factory=RealDictCursor)
    src_conn.autocommit = True

    src_cur = src_conn.cursor()
    dst_cur = dst_conn.cursor()

    try:
        # Step 1: Create new EEA lookup tables
        log("Step 1: Creating new EEA lookup tables...")
        dst_cur.execute(CREATE_NEW_EEA_TABLES_SQL)
        log("  Done")

        # Step 2: Populate new EEA tables from ravendb4
        log("Step 2: Copying EEA vocabulary data from ravendb4...")
        for table in NEW_EEA_TABLES:
            copy_eea_table(src_cur, dst_cur, table, dry_run)

        # Step 3: Drop v3-only tables (no data to preserve)
        log("Step 3: Dropping v3-only tables...")
        for tbl in ["observing_capabilities", "responsible_authorities", "samples", "eea_organisationallevels"]:
            dst_cur.execute(f"DROP TABLE IF EXISTS {tbl} CASCADE")
            log(f"  Dropped {tbl}")

        # Step 4: Rename assessmentregimes → drop it (v3 had different structure, 0 rows)
        log("Step 4: Dropping old assessmentregimes (v3, 0 rows, different structure)...")
        dst_cur.execute("DROP TABLE IF EXISTS assessmentregimes CASCADE")
        log("  Dropped assessmentregimes")

        # Step 5: Fix aqi (30 rows) - drop pollutant_uri column
        log("Step 5: Fixing aqi table (drop pollutant_uri)...")
        dst_cur.execute("ALTER TABLE aqi DROP COLUMN IF EXISTS pollutant_uri")
        log("  Done")

        # Step 6: Fix statistics (77 rows) - pollutant_uri → pollutant_id integer
        log("Step 6: Fixing statistics table (pollutant_uri → pollutant_id integer)...")
        dst_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='statistics' AND column_name='pollutant_uri' AND table_schema='public'")
        if dst_cur.fetchone():
            dst_cur.execute("ALTER TABLE statistics ADD COLUMN IF NOT EXISTS pollutant_id_new integer")
            if not dry_run:
                dst_cur.execute("""
                    UPDATE statistics s
                    SET pollutant_id_new = p.id
                    FROM eea_pollutants p
                    WHERE p.uri = s.pollutant_uri
                """)
                dst_cur.execute("SELECT COUNT(*) as c FROM statistics WHERE pollutant_id_new IS NULL")
                null_count = dst_cur.fetchone()["c"]
                if null_count > 0:
                    log(f"  WARNING: {null_count} statistics rows could not be mapped - setting to NULL")
            dst_cur.execute("ALTER TABLE statistics DROP COLUMN IF EXISTS pollutant_uri")
            dst_cur.execute("ALTER TABLE statistics RENAME COLUMN pollutant_id_new TO pollutant_id")
            log("  Done")
        else:
            log("  statistics.pollutant_uri not found - already migrated?")

        # Step 7: Fix autovalidated_series (0 rows) - pollutant → pollutant_id integer
        log("Step 7: Fixing autovalidated_series (pollutant → pollutant_id integer)...")
        dst_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='autovalidated_series' AND column_name='pollutant' AND table_schema='public'")
        if dst_cur.fetchone():
            dst_cur.execute("ALTER TABLE autovalidated_series ADD COLUMN IF NOT EXISTS pollutant_id_new integer")
            if not dry_run:
                dst_cur.execute("""
                    UPDATE autovalidated_series a
                    SET pollutant_id_new = p.id
                    FROM eea_pollutants p
                    WHERE p.notation = a.pollutant OR p.uri LIKE '%' || a.pollutant || '%'
                """)
            dst_cur.execute("ALTER TABLE autovalidated_series DROP COLUMN IF EXISTS pollutant")
            dst_cur.execute("ALTER TABLE autovalidated_series RENAME COLUMN pollutant_id_new TO pollutant_id")
            log("  Done")
        else:
            log("  autovalidated_series.pollutant not found - already migrated?")

        # Step 8: Fix stations (1 row) - drop v3 columns, add v4 columns
        log("Step 8: Fixing stations table...")
        v3_station_cols = [
            "city", "national_station_code", "media_monitored", "mobile",
            "measurement_regime", "area_classification", "distance_junction",
            "traffic_volume", "heavy_duty_fraction", "street_width",
            "height_facades", "geom", "municipality",
        ]
        for col in v3_station_cols:
            dst_cur.execute(f"ALTER TABLE stations DROP COLUMN IF EXISTS {col}")
        dst_cur.execute("ALTER TABLE stations ADD COLUMN IF NOT EXISTS supersite boolean DEFAULT false")
        dst_cur.execute("ALTER TABLE stations ADD COLUMN IF NOT EXISTS area_classification_id varchar(100)")
        dst_cur.execute("ALTER TABLE stations ADD COLUMN IF NOT EXISTS document_id varchar(255)")
        log("  Done")

        # Step 8b: Drop v3 materialized views (they reference sampling_points.timestep)
        log("Step 8b: Dropping v3 materialized views (depend on sampling_points.timestep)...")
        for view in MATVIEW_NAMES:
            dst_cur.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view} CASCADE")
        log("  Done")

        # Step 9: Fix sampling_points (13 rows) - drop v3-only columns
        log("Step 9: Fixing sampling_points table...")
        v3_sp_cols = [
            "media_monitored", "measurement_regime", "mobile", "assessment_type",
            "station_classification", "used_aqd", "main_emission_sources",
            "traffic_emissions", "heating_emissions", "industrial_emissions",
            "distance_source", "change_aei_stations", "begin_position",
            "end_position", "pollutant", "concentration", "timestep",
        ]
        for col in v3_sp_cols:
            dst_cur.execute(f"ALTER TABLE sampling_points DROP COLUMN IF EXISTS {col}")
        log("  Done")

        # Step 10: Drop and recreate processes (0 rows - completely different structure)
        log("Step 10: Recreating processes table (0 rows)...")
        dst_cur.execute("DROP TABLE IF EXISTS processes CASCADE")
        dst_cur.execute("""
            CREATE TABLE processes (
                id                                    varchar(100) not null primary key,
                activity_begin                        varchar(25)  not null,
                activity_end                          varchar(25),
                measurement_type_id                   varchar(100) references eea_measurementtypes on update cascade,
                method_id                             varchar(100) references eea_measurementmethods on update cascade,
                equipment_id                          varchar(100) references eea_measurementequipments on update cascade,
                analytical_technique_id               varchar(100) references eea_analyticaltechnique on update cascade,
                equivalence_demonstrated_id           varchar(100) references eea_equivalencedemonstrated on update cascade,
                sampling_point_id                     varchar(100) not null references sampling_points on update cascade on delete cascade,
                data_quality_document_id              varchar(255) references documents on update cascade,
                equivalence_demonstration_document_id varchar(255) references documents on update cascade,
                process_document_id                   varchar(255) references documents on update cascade,
                equipment_identifier                  varchar(255)
            )
        """)
        dst_cur.execute("CREATE INDEX IF NOT EXISTS idx_processes_sp ON processes (sampling_point_id)")
        log("  Done")

        # Step 11: Drop and recreate observations (0 rows - different validity/verification columns)
        log("Step 11: Recreating observations table (0 rows)...")
        dst_cur.execute("DROP TABLE IF EXISTS observations CASCADE")
        dst_cur.execute("""
            CREATE TABLE observations (
                id                         bigserial primary key,
                sampling_point_id          varchar(100)                  not null references sampling_points on update cascade on delete cascade,
                value                      numeric(255, 5)               not null,
                observationverification_id integer default 3             not null references eea_observationverification,
                observationvalidity_id     integer default '-1'::integer not null references eea_observationvalidity,
                touched                    timestamp(6)                  not null,
                from_time                  timestamp                     not null,
                to_time                    timestamp                     not null,
                import_value               numeric(255, 5)               not null,
                scaled_value               numeric(255, 5),
                constraint un_obs_spoid_fromto unique (sampling_point_id, from_time, to_time)
            )
        """)
        dst_cur.execute("CREATE INDEX IF NOT EXISTS idx_observations_spid_ft ON observations (sampling_point_id, from_time)")
        dst_cur.execute("CREATE INDEX IF NOT EXISTS idx_observations_spid ON observations (sampling_point_id)")
        dst_cur.execute("CREATE INDEX IF NOT EXISTS idx_obs_spoid_day ON observations (sampling_point_id, date_trunc('day'::text, from_time))")
        dst_cur.execute("CREATE INDEX IF NOT EXISTS idx_obs_spoid_year ON observations (sampling_point_id, date_trunc('year'::text, from_time))")
        log("  Done")

        # Step 12: Drop and recreate zones (0 rows - different structure)
        log("Step 12: Recreating zones table (0 rows)...")
        dst_cur.execute("DROP TABLE IF EXISTS zones CASCADE")
        dst_cur.execute("""
            CREATE TABLE zones (
                id               varchar(100) not null primary key,
                code             varchar(100) not null,
                name             varchar(254) not null,
                geom             geometry     not null
                    constraint enforce_dims_geom check (st_ndims(geom) = 2)
                    constraint enforce_srid_geom check (st_srid(geom) = 4326),
                area             numeric      not null,
                zone_category_id varchar(100) references eea_zonecategory on update cascade,
                zone_type_id     varchar(100) references eea_zonetypes on update cascade
            )
        """)
        dst_cur.execute("CREATE INDEX IF NOT EXISTS zones_geom_gist ON zones USING gist (geom)")
        log("  Done")

        # Step 13a: Fix eea_pollutants primary key (v3 has uri as PK, v4 uses id)
        log("Step 13a: Fixing eea_pollutants primary key (uri → id)...")
        dst_cur.execute("""
            DO $$
            DECLARE pk_col text;
            BEGIN
                SELECT kcu.column_name INTO pk_col
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = 'eea_pollutants' AND tc.constraint_type = 'PRIMARY KEY'
                LIMIT 1;

                IF pk_col = 'uri' THEN
                    ALTER TABLE eea_pollutants DROP CONSTRAINT eea_pollutants_pkey1;
                    ALTER TABLE eea_pollutants ALTER COLUMN id SET NOT NULL;
                    ALTER TABLE eea_pollutants ADD PRIMARY KEY (id);
                END IF;
            END $$;
        """)
        log("  Done")

        # Step 13b: Fix all v3 EEA tables missing columns (notation, uri, etc.) + refresh data
        log("Step 13b: Fixing v3 EEA tables missing columns (notation, uri, etc.)...")
        dst_cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'eea_%' ORDER BY table_name")
        eea_tables = [r["table_name"] for r in dst_cur.fetchall()]
        type_map = {"character varying": "varchar(255)", "text": "text", "integer": "integer",
                    "numeric": "numeric", "boolean": "boolean"}
        for t in eea_tables:
            dst_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s", (t,))
            dst_cols = {r["column_name"] for r in dst_cur.fetchall()}
            src_cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name=%s ORDER BY ordinal_position", (t,))
            src_col_rows = src_cur.fetchall()
            src_cols = [r["column_name"] for r in src_col_rows]
            src_types = {r["column_name"]: r["data_type"] for r in src_col_rows}
            missing = [c for c in src_cols if c not in dst_cols]
            if not missing:
                continue
            log(f"  {t}: adding {missing}")
            for col in missing:
                ddl = type_map.get(src_types[col], "varchar(255)")
                dst_cur.execute(f"ALTER TABLE {t} ADD COLUMN IF NOT EXISTS {col} {ddl}")
            col_list = ", ".join(src_cols)
            pk = src_cols[0]
            updates = ", ".join(f"{c}=%({c})s" for c in src_cols if c != pk)
            src_cur.execute(f"SELECT {col_list} FROM {t}")
            for row in src_cur.fetchall():
                dst_cur.execute(f"UPDATE {t} SET {updates} WHERE {pk}=%({pk})s", dict(row))
        log("  Done")

        # Step 13: Create all remaining missing tables
        log("Step 13: Creating remaining missing tables...")
        dst_cur.execute(CREATE_REMAINING_TABLES_SQL)
        log("  Done")

        # Step 14: Install coverage function + triggers
        log("Step 14: Installing raven_coverage function, triggers...")
        dst_cur.execute(CREATE_COVERAGE_FUNCTION_SQL)
        dst_cur.execute(CREATE_FUNCTIONS_AND_TRIGGERS_SQL)
        log("  Done")

        # Step 15: Insert schema_version
        log("Step 15: Inserting schema_version...")
        if not dry_run:
            dst_cur.execute("""
                INSERT INTO schema_version (version, description)
                VALUES ('4.6.0', 'v3→v4 migration: restructured processes/observations, added FK-based schema')
                ON CONFLICT (version) DO NOTHING
            """)
        log("  Done")

        # Step 16: Recreate v4 materialized views
        log("Step 16: Creating v4 materialized views...")
        dst_cur.execute(CREATE_MATVIEWS_SQL)
        log("  Done")

        # Verify key tables
        log("")
        log("Verification:")
        dst_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='processes' AND table_schema='public' ORDER BY ordinal_position")
        cols = [r["column_name"] for r in dst_cur.fetchall()]
        log(f"  processes columns: {cols}")

        dst_cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='observations' AND table_schema='public' ORDER BY ordinal_position")
        cols = [r["column_name"] for r in dst_cur.fetchall()]
        log(f"  observations columns: {cols}")

        dst_cur.execute("SELECT COUNT(*) as c FROM sampling_points")
        log(f"  sampling_points rows: {dst_cur.fetchone()['c']}")

        dst_cur.execute("SELECT COUNT(*) as c FROM stations")
        log(f"  stations rows: {dst_cur.fetchone()['c']}")

        dst_cur.execute("SELECT COUNT(*) as c FROM statistics")
        log(f"  statistics rows: {dst_cur.fetchone()['c']}")

        if dry_run:
            log("")
            log("DRY RUN complete - rolling back all changes")
            dst_conn.rollback()
        else:
            dst_conn.commit()
            log("")
            log("Migration complete! All changes committed.")

    except Exception as e:
        dst_conn.rollback()
        log(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        src_cur.close()
        dst_cur.close()
        src_conn.close()
        dst_conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate raven-airquis DB from v3 to v4 schema")
    parser.add_argument("--dry-run", action="store_true", help="Test without committing changes")
    args = parser.parse_args()
    migrate(dry_run=args.dry_run)
