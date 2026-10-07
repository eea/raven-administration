-- ===========================================================================
-- 025 — the pre-aggregates and sampling_point_groups become part of the schema
--
-- Statistics, Exceedances and the AQR3 compliance numbers read observations
-- through ten materialized views (observations_year, _day, _day_8hmax, _aot40v,
-- ...) and two functions, raven_coverage() and raven_refresh_aggregates(). None
-- of it was in schema.sql or any migration, and sampling_point_groups -- used by
-- processing/calculate, the sampling point group screen and QC validation -- had
-- no DDL in the repository at all. Four defects follow from that:
--
-- 1. MISSING EVERYWHERE NEW. Every database built from schema.sql + migrations,
--    every migrate-wizard run included, had none of it. Nothing failed loudly:
--    evaluate_exceedances() catches the "relation does not exist" per statistic
--    and returns zero rows, so Malta on dev-raven4 showed an empty Exceedances
--    page for every pollutant while holding 2.1M observations.
--
-- 2. THE ONLY SOURCE WAS STALE. sql/pre_aggregates.sql, the README's manual step,
--    still read sampling_points.timestep, validation_flag and verification_flag,
--    all renamed in v4 (time_resolution_id, observationvalidity_id,
--    observationverification_id), so it failed on every v4 database. Its
--    observations_year also averaged raw values, where the deployed databases
--    average hourly means. The definitions below are the deployed ones: pg_dump of
--    dev-raven4 before Malta replaced it, identical in meaning to raven-airquis
--    (built by scripts-nilu/migrate_airquis.py) -- PostgreSQL keeps a view
--    working across a column rename, which is why those two kept running.
--
-- 3. REFRESH NEVER WORKED. raven_refresh_aggregates() uses REFRESH ... CONCURRENTLY,
--    which requires a unique index, and raven-airquis has no index on any view.
--    The cron job (cron/refresh_views.py) prints the error and exits 0, so
--    raven-airquis's aggregates stood still from their creation on 2026-09-09
--    while observations kept arriving. Each view now gets a unique index on
--    (sampling_point_id, time), which is what every one is grouped by, under
--    PostgreSQL's default name: the old dev-raven4 had exactly these, made by
--    hand, and IF NOT EXISTS keeps them instead of adding duplicates.
--
-- 4. TWO VIEWS WERE NOT IN THE REFRESH. raven-airquis's raven_refresh_aggregates()
--    (from pre_aggregates.sql) omitted observations_year_hour and
--    observations_year_day (P1Y-hr-max/min, daily-based annual statistics). It now
--    refreshes all ten, as the old dev-raven4's hand-edited copy already did.
--
-- Cost at boot: where a view exists (raven-airquis) it is left alone -- only its
-- index is built, over the aggregate rows, not over observations. Where it is
-- missing it is created WITH DATA, i.e. computed from observations during the API
-- pod's boot-time migration; under a minute for Malta's 2.1M rows. Existing but
-- stale views are deliberately NOT refreshed here: on raven-airquis that would
-- hold the pod's startup for the length of a full recompute. The next cron run,
-- or Misc -> Pre-aggregation, does it -- and now succeeds.
--
-- Idempotent. schema.sql carries the same DDL and seeds this version, and
-- sql/pre_aggregates.sql is regenerated from the same definitions to drop and
-- rebuild the views from scratch.
-- ===========================================================================

begin;

CREATE INDEX IF NOT EXISTS idx_obs_spoid_day ON public.observations USING btree (sampling_point_id, date_trunc('day'::text, from_time));

------------------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_obs_spoid_year ON public.observations USING btree (sampling_point_id, date_trunc('year'::text, from_time));

------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.raven_coverage(datetime timestamp without time zone, count integer, timestep integer, coverage_type text DEFAULT 'year'::text) RETURNS numeric
    LANGUAGE plpgsql
    AS $$
declare y integer;
declare is_leap_year boolean;
declare seconds integer;
begin
    seconds := 31536000;
    y := extract(year from datetime);
    is_leap_year := (y % 4 = 0) and (y % 100 <> 0 or y % 400 = 0);

    if is_leap_year then
        seconds := 31622400;
    end if;

    if coverage_type = 'aot40v' then
        seconds := 3974400;
    elsif coverage_type = 'aot40f' then
        seconds :=  7905600;
    elsif coverage_type = 'winterseason' and not is_leap_year then
        seconds := 15724800;
    elsif coverage_type = 'winterseason' and  is_leap_year then
        seconds := 15811200;
    elsif coverage_type = 'summeryear' then
        seconds := 15811200;
    elsif coverage_type = 'winteryear' and not is_leap_year then
        seconds := 15724800;
    elsif coverage_type = 'winteryear' and  is_leap_year then
        seconds := 15811200;
    elsif coverage_type = 'day' then
        seconds := 86400;
    elsif coverage_type = 'hour' then
        seconds := 3600;
    end if;

    if timestep > seconds then
        return 0;
    end if;

    return round((count::numeric*100) / (seconds/timestep),10);
end
$$;

------------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION public.raven_refresh_aggregates() RETURNS void
    LANGUAGE plpgsql
    AS $$
begin
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_year;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_aot40f;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_aot40v;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_winter_season;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_summer_year;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_winter_year;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_day;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_day_8hmax;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_year_hour;
    REFRESH MATERIALIZED VIEW CONCURRENTLY observations_year_day;
end
$$;

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_year AS
 SELECT yearly.sampling_point_id,
    yearly.timestep,
    yearly."time",
    yearly.val,
    yearly.min,
    yearly.max,
    yearly.count_all,
    yearly.count_valid,
    yearly.count_verified,
    public.raven_coverage(yearly."time", (yearly.count_valid)::integer, yearly.timestep, 'year'::text) AS cov,
    now() AS created
   FROM ( WITH timeseries AS (
                 SELECT s.id AS sampling_point_id,
                    t_1.timestep
                   FROM public.sampling_points s,
                    public.eea_times t_1
                  WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
                )
         SELECT hourly.sampling_point_id,
            t.timestep,
            date_trunc('year'::text, hourly.datetime) AS "time",
            avg(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS val,
            min(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS min,
            max(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS max,
            count(*) AS count_all,
            count(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN 1
                    ELSE NULL::integer
                END) AS count_valid,
            count(
                CASE
                    WHEN (hourly.count_verified = hourly.count_all) THEN 1
                    ELSE 0
                END) AS count_verified
           FROM ( SELECT observations.sampling_point_id,
                    date_trunc('hour'::text, observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
                    (count(observations.value))::integer AS count_all,
                    (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
                    (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
                   FROM public.observations
                  GROUP BY observations.sampling_point_id, (date_trunc('hour'::text, observations.from_time))) hourly,
            timeseries t
          WHERE ((hourly.sampling_point_id)::text = (t.sampling_point_id)::text)
          GROUP BY hourly.sampling_point_id, (date_trunc('year'::text, hourly.datetime)), t.timestep) yearly
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_year_sampling_point_id_time_idx
    ON public.observations_year (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_aot40f AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        )
 SELECT a.sampling_point_id,
    a."time",
        CASE
            WHEN (public.raven_coverage(a."time", a.count_valid, t.timestep, 'aot40f'::text) < (100)::numeric) THEN round(((a.val * (a.count_all)::numeric) / (a.count_valid)::numeric), 10)
            ELSE a.val
        END AS val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'aot40f'::text) AS cov,
    now() AS created
   FROM ( SELECT observations.sampling_point_id,
            date_trunc('year'::text, observations.from_time) AS "time",
            round(sum((observations.value - (80)::numeric)) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS val,
            round(min(observations.value) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS min,
            round(max(observations.value) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS max,
            (count(observations.value))::integer AS count_all,
            (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
            (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
           FROM public.observations
          WHERE ((to_char(observations.from_time, 'MM'::text) = ANY (ARRAY['04'::text, '05'::text, '06'::text, '07'::text, '08'::text, '09'::text])) AND (to_char(observations.from_time, 'HH24'::text) = ANY (ARRAY['08'::text, '09'::text, '10'::text, '11'::text, '12'::text, '13'::text, '14'::text, '15'::text, '16'::text, '17'::text, '18'::text, '19'::text])))
          GROUP BY observations.sampling_point_id, (date_trunc('year'::text, observations.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_aot40f_sampling_point_id_time_idx
    ON public.observations_aot40f (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_aot40v AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        )
 SELECT a.sampling_point_id,
    a."time",
        CASE
            WHEN (public.raven_coverage(a."time", a.count_valid, t.timestep, 'aot40v'::text) < (100)::numeric) THEN round(((a.val * (a.count_all)::numeric) / (a.count_valid)::numeric), 10)
            ELSE a.val
        END AS val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'aot40v'::text) AS cov,
    now() AS created
   FROM ( SELECT observations.sampling_point_id,
            date_trunc('year'::text, observations.from_time) AS "time",
            round(sum((observations.value - (80)::numeric)) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS val,
            round(min(observations.value) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS min,
            round(max(observations.value) FILTER (WHERE ((observations.observationvalidity_id >= 1) AND ((observations.value - (80)::numeric) > (0)::numeric))), 10) AS max,
            (count(observations.value))::integer AS count_all,
            (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
            (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
           FROM public.observations
          WHERE ((to_char(observations.from_time, 'MM'::text) = ANY (ARRAY['05'::text, '06'::text, '07'::text])) AND (to_char(observations.from_time, 'HH24'::text) = ANY (ARRAY['08'::text, '09'::text, '10'::text, '11'::text, '12'::text, '13'::text, '14'::text, '15'::text, '16'::text, '17'::text, '18'::text, '19'::text])))
          GROUP BY observations.sampling_point_id, (date_trunc('year'::text, observations.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_aot40v_sampling_point_id_time_idx
    ON public.observations_aot40v (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_winter_season AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        ), timevalues AS (
         SELECT
                CASE date_part('month'::text, o.from_time)
                    WHEN 10 THEN (o.from_time + '1 year'::interval)
                    WHEN 11 THEN (o.from_time + '1 year'::interval)
                    WHEN 12 THEN (o.from_time + '1 year'::interval)
                    ELSE o.from_time
                END AS from_time,
            o.sampling_point_id,
            o.value,
            o.observationvalidity_id,
            o.observationverification_id
           FROM public.observations o
          WHERE (date_part('month'::text, o.from_time) = ANY (ARRAY[(1)::double precision, (2)::double precision, (3)::double precision, (10)::double precision, (11)::double precision, (12)::double precision]))
        )
 SELECT a.sampling_point_id,
    a."time",
    a.val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'winterseason'::text) AS cov,
    now() AS created
   FROM ( SELECT timevalues.sampling_point_id,
            date_trunc('year'::text, timevalues.from_time) AS "time",
            round(avg(timevalues.value) FILTER (WHERE (timevalues.observationvalidity_id = ANY (ARRAY[1, 2, 3]))), 10) AS val,
            round(min(timevalues.value) FILTER (WHERE (timevalues.observationvalidity_id = ANY (ARRAY[1, 2, 3]))), 10) AS min,
            round(max(timevalues.value) FILTER (WHERE (timevalues.observationvalidity_id = ANY (ARRAY[1, 2, 3]))), 10) AS max,
            (count(timevalues.value))::integer AS count_all,
            (count(timevalues.value) FILTER (WHERE (timevalues.observationvalidity_id = ANY (ARRAY[1, 2, 3]))))::integer AS count_valid,
            (count(*) FILTER (WHERE (timevalues.observationverification_id = 1)))::integer AS count_verified
           FROM timevalues
          GROUP BY timevalues.sampling_point_id, (date_trunc('year'::text, timevalues.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_winter_season_sampling_point_id_time_idx
    ON public.observations_winter_season (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_summer_year AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        )
 SELECT a.sampling_point_id,
    a."time",
    a.val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'summeryear'::text) AS cov,
    now() AS created
   FROM ( SELECT observations.sampling_point_id,
            date_trunc('year'::text, observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
            round(min(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS min,
            round(max(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS max,
            (count(observations.value))::integer AS count_all,
            (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
            (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
           FROM public.observations
          WHERE (to_char(observations.from_time, 'MM'::text) = ANY (ARRAY['04'::text, '05'::text, '06'::text, '07'::text, '08'::text, '09'::text]))
          GROUP BY observations.sampling_point_id, (date_trunc('year'::text, observations.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_summer_year_sampling_point_id_time_idx
    ON public.observations_summer_year (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_winter_year AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        )
 SELECT a.sampling_point_id,
    a."time",
    a.val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'winteryear'::text) AS cov,
    now() AS created
   FROM ( SELECT observations.sampling_point_id,
            date_trunc('year'::text, observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
            round(min(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS min,
            round(max(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS max,
            (count(observations.value))::integer AS count_all,
            (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
            (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
           FROM public.observations
          WHERE (to_char(observations.from_time, 'MM'::text) = ANY (ARRAY['01'::text, '02'::text, '03'::text, '10'::text, '11'::text, '12'::text]))
          GROUP BY observations.sampling_point_id, (date_trunc('year'::text, observations.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_winter_year_sampling_point_id_time_idx
    ON public.observations_winter_year (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_day AS
 WITH timeseries AS (
         SELECT s.id AS sampling_point_id,
            t_1.timestep
           FROM public.sampling_points s,
            public.eea_times t_1
          WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
        )
 SELECT a.sampling_point_id,
    a."time",
    a.val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    public.raven_coverage(a."time", a.count_valid, t.timestep, 'day'::text) AS cov,
    now() AS created
   FROM ( SELECT observations.sampling_point_id,
            date_trunc('day'::text, observations.from_time) AS "time",
            round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
            round(min(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS min,
            round(max(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS max,
            (count(observations.value))::integer AS count_all,
            (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
            (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
           FROM public.observations
          GROUP BY observations.sampling_point_id, (date_trunc('day'::text, observations.from_time))) a,
    timeseries t
  WHERE ((a.sampling_point_id)::text = (t.sampling_point_id)::text)
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_day_sampling_point_id_time_idx
    ON public.observations_day (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_day_8hmax AS
 SELECT running_8hours_max.sampling_point_id,
    running_8hours_max.timestep,
    running_8hours_max."time",
    running_8hours_max.val,
    running_8hours_max.min,
    running_8hours_max.max,
    running_8hours_max.count_all,
    running_8hours_max.count_valid,
    running_8hours_max.count_verified,
    public.raven_coverage(running_8hours_max."time", (running_8hours_max.count_valid)::integer, running_8hours_max.timestep, 'day'::text) AS cov,
    now() AS created
   FROM ( WITH timeseries AS (
                 SELECT s.id AS sampling_point_id,
                    t_1.timestep
                   FROM public.sampling_points s,
                    public.eea_times t_1
                  WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
                )
         SELECT running_8hours.sampling_point_id,
            t.timestep,
            date_trunc('day'::text, running_8hours.datetime) AS "time",
            max(
                CASE
                    WHEN ((running_8hours.count_valid)::double precision >= ((0.75 * (28800.0 / (t.timestep)::numeric)))::double precision) THEN running_8hours.val
                    ELSE NULL::numeric
                END) AS val,
            min(
                CASE
                    WHEN ((running_8hours.count_valid)::double precision >= ((0.75 * (28800.0 / (t.timestep)::numeric)))::double precision) THEN running_8hours.val
                    ELSE NULL::numeric
                END) AS min,
            max(
                CASE
                    WHEN ((running_8hours.count_valid)::double precision >= ((0.75 * (28800.0 / (t.timestep)::numeric)))::double precision) THEN running_8hours.val
                    ELSE NULL::numeric
                END) AS max,
            count(*) AS count_all,
            count(
                CASE
                    WHEN ((running_8hours.count_valid)::double precision >= ((0.75 * (28800.0 / (t.timestep)::numeric)))::double precision) THEN 1
                    ELSE NULL::integer
                END) AS count_valid,
            count(
                CASE
                    WHEN (running_8hours.count_verified = running_8hours.count_all) THEN 1
                    ELSE 0
                END) AS count_verified
           FROM ( SELECT o.from_time AS datetime,
                    o.sampling_point_id,
                    avg(
                        CASE
                            WHEN (o.observationvalidity_id >= 1) THEN o.value
                            ELSE NULL::numeric
                        END) OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00'::interval PRECEDING AND CURRENT ROW) AS val,
                    count(*) OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00'::interval PRECEDING AND CURRENT ROW) AS count_all,
                    count(
                        CASE
                            WHEN (o.observationvalidity_id >= 1) THEN 1
                            ELSE NULL::integer
                        END) OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00'::interval PRECEDING AND CURRENT ROW) AS count_valid,
                    count(
                        CASE
                            WHEN (o.observationverification_id = 1) THEN 1
                            ELSE NULL::integer
                        END) OVER (PARTITION BY o.sampling_point_id ORDER BY o.from_time RANGE BETWEEN '07:00:00'::interval PRECEDING AND CURRENT ROW) AS count_verified
                   FROM public.observations o) running_8hours,
            timeseries t
          WHERE ((running_8hours.sampling_point_id)::text = (t.sampling_point_id)::text)
          GROUP BY running_8hours.sampling_point_id, (date_trunc('day'::text, running_8hours.datetime)), t.timestep) running_8hours_max
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_day_8hmax_sampling_point_id_time_idx
    ON public.observations_day_8hmax (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_year_hour AS
 SELECT yearly.sampling_point_id,
    yearly.timestep,
    yearly."time",
    yearly.val,
    yearly.min,
    yearly.max,
    yearly.count_all,
    yearly.count_valid,
    yearly.count_verified,
    public.raven_coverage(yearly."time", (yearly.count_valid)::integer, yearly.timestep, 'year'::text) AS cov,
    now() AS created
   FROM ( WITH timeseries AS (
                 SELECT s.id AS sampling_point_id,
                    t_1.timestep
                   FROM public.sampling_points s,
                    public.eea_times t_1
                  WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
                )
         SELECT hourly.sampling_point_id,
            t.timestep,
            date_trunc('year'::text, hourly.datetime) AS "time",
            avg(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS val,
            min(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS min,
            max(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN hourly.val
                    ELSE NULL::numeric
                END) AS max,
            count(*) AS count_all,
            count(
                CASE
                    WHEN ((hourly.count_valid)::double precision >= ((0.75 * (3600.0 / (t.timestep)::numeric)))::double precision) THEN 1
                    ELSE NULL::integer
                END) AS count_valid,
            count(
                CASE
                    WHEN (hourly.count_verified = hourly.count_all) THEN 1
                    ELSE 0
                END) AS count_verified
           FROM ( SELECT observations.sampling_point_id,
                    date_trunc('hour'::text, observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
                    (count(observations.value))::integer AS count_all,
                    (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
                    (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
                   FROM public.observations
                  GROUP BY observations.sampling_point_id, (date_trunc('hour'::text, observations.from_time))) hourly,
            timeseries t
          WHERE ((hourly.sampling_point_id)::text = (t.sampling_point_id)::text)
          GROUP BY hourly.sampling_point_id, (date_trunc('year'::text, hourly.datetime)), t.timestep) yearly
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_year_hour_sampling_point_id_time_idx
    ON public.observations_year_hour (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE MATERIALIZED VIEW IF NOT EXISTS public.observations_year_day AS
 SELECT yearly.sampling_point_id,
    yearly.timestep,
    yearly."time",
    yearly.val,
    yearly.min,
    yearly.max,
    yearly.p99,
    yearly.count_all,
    yearly.count_valid,
    yearly.count_verified,
    public.raven_coverage(yearly."time", (yearly.count_valid)::integer, yearly.timestep, 'year'::text) AS cov,
    now() AS created
   FROM ( WITH timeseries AS (
                 SELECT s.id AS sampling_point_id,
                    t_1.timestep
                   FROM public.sampling_points s,
                    public.eea_times t_1
                  WHERE ((s.time_resolution_id)::text = (t_1.id)::text)
                )
         SELECT daily.sampling_point_id,
            t.timestep,
            date_trunc('year'::text, daily.datetime) AS "time",
            avg(
                CASE
                    WHEN ((daily.count_valid)::double precision >= ((0.75 * (86400.0 / (t.timestep)::numeric)))::double precision) THEN daily.val
                    ELSE NULL::numeric
                END) AS val,
            min(
                CASE
                    WHEN ((daily.count_valid)::double precision >= ((0.75 * (86400.0 / (t.timestep)::numeric)))::double precision) THEN daily.val
                    ELSE NULL::numeric
                END) AS min,
            max(
                CASE
                    WHEN ((daily.count_valid)::double precision >= ((0.75 * (86400.0 / (t.timestep)::numeric)))::double precision) THEN daily.val
                    ELSE NULL::numeric
                END) AS max,
            (percentile_cont((0.99)::double precision) WITHIN GROUP (ORDER BY ((
                CASE
                    WHEN ((daily.count_valid)::double precision >= ((0.75 * (86400.0 / (t.timestep)::numeric)))::double precision) THEN daily.val
                    ELSE NULL::numeric
                END)::double precision)))::numeric AS p99,
            count(*) AS count_all,
            count(
                CASE
                    WHEN ((daily.count_valid)::double precision >= ((0.75 * (86400.0 / (t.timestep)::numeric)))::double precision) THEN 1
                    ELSE NULL::integer
                END) AS count_valid,
            count(
                CASE
                    WHEN (daily.count_verified = daily.count_all) THEN 1
                    ELSE 0
                END) AS count_verified
           FROM ( SELECT observations.sampling_point_id,
                    date_trunc('day'::text, observations.from_time) AS datetime,
                    round(avg(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)), 10) AS val,
                    (count(observations.value))::integer AS count_all,
                    (count(observations.value) FILTER (WHERE (observations.observationvalidity_id >= 1)))::integer AS count_valid,
                    (count(*) FILTER (WHERE (observations.observationverification_id = 1)))::integer AS count_verified
                   FROM public.observations
                  GROUP BY observations.sampling_point_id, (date_trunc('day'::text, observations.from_time))) daily,
            timeseries t
          WHERE ((daily.sampling_point_id)::text = (t.sampling_point_id)::text)
          GROUP BY daily.sampling_point_id, (date_trunc('year'::text, daily.datetime)), t.timestep) yearly
  WITH DATA;

CREATE UNIQUE INDEX IF NOT EXISTS observations_year_day_sampling_point_id_time_idx
    ON public.observations_year_day (sampling_point_id, "time");

------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.sampling_point_groups
(
    group_id          bigint       NOT NULL,
    sampling_point_id varchar(100) NOT NULL,
    CONSTRAINT sampling_point_groups_pkey PRIMARY KEY (sampling_point_id),
    CONSTRAINT sampling_point_groups_sp_fk FOREIGN KEY (sampling_point_id)
        REFERENCES public.sampling_points (id)
);

insert into schema_version (version, description)
values ('4.502.25', 'pre-aggregate materialized views with unique indexes, raven_coverage(), '
                    'raven_refresh_aggregates() over all ten, and sampling_point_groups')
on conflict (version) do nothing;

commit;
