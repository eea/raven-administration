------------------------------------------------------------------------------------

create index IF NOT EXISTS idx_obs_spoid_year on public.observations (sampling_point_id, date_trunc('year'::text, from_time));
create index IF NOT EXISTS idx_obs_spoid_day on public.observations (sampling_point_id, date_trunc('day'::text, from_time));

------------------------------------------------------------------------------------

create or replace function raven_coverage(datetime timestamp,count integer, timestep integer,coverage_type text default 'year')
returns numeric(10) as $$
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
    end if;

    if timestep > seconds then
        return 0;
    end if;

    return round((count::numeric*100) / (seconds/timestep),10);
end
$$ language plpgsql;


------------------------------------------------------------------------------------


create or replace function raven_refresh_aggregates()
returns void as $$
begin
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_year;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_aot40f;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_aot40v;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_winter_season;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_summer_year;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_winter_year;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_day;
    REFRESH MATERIALIZED VIEW  CONCURRENTLY  observations_day_8hmax;
end
$$ language plpgsql;



------------------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS observations_year;
create materialized view observations_year as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.*,
    raven_coverage(time,count_valid,t.timestep) as cov,
    now() as created
from (select sampling_point_id,
             date_trunc('year', from_time)                                     as time,
             round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
             round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
             round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
             count(value)          ::int                                            AS count_all,
             count(value) FILTER (WHERE validation_flag >= 1) ::int         AS count_valid,
             count(*) FILTER (WHERE verification_flag = 1)  ::int                   as count_verified
      from observations
      group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;


CREATE INDEX idx_obs_year_id_time
on observations_year (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_year_id_time
on observations_year (sampling_point_id,time);

------------------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS observations_winter_year;
create materialized view observations_winter_year as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.*,
    raven_coverage(a.time, a.count_valid::int,t.timestep,'winteryear') as cov,
    now() as created
from (
    select
        sampling_point_id,
        date_trunc('year', from_time)                                     as time,
        round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
        round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
        round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
        count(value)          ::int                                            AS count_all,
        count(value) FILTER (WHERE validation_flag >= 1) ::int         AS count_valid,
        count(*) FILTER (WHERE verification_flag = 1)  ::int                   as count_verified
    from observations
    where 1 = 1
    and to_char(from_time, 'MM') IN ('01','02','03','10','11','12')
    group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;


CREATE INDEX idx_obs_winter_year_id_time
on observations_winter_year (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_winter_year_id_time
on observations_winter_year (sampling_point_id,time);


------------------------------------------------------------------------------------
DROP MATERIALIZED VIEW IF EXISTS observations_winter_season;
create materialized view observations_winter_season as
with
    timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id),
    timevalues as
         (SELECT CASE EXTRACT(MONTH FROM o.from_time)
                     WHEN 10 THEN (o.from_time + interval '12 MONTH')
                     WHEN 11 THEN (o.from_time + interval '12 MONTH')
                     WHEN 12 THEN (o.from_time + interval '12 MONTH')
                     ELSE o.from_time
                     END as from_time,
                    o.sampling_point_id,
                    o.value,
                    o.validation_flag,
                    o.verification_flag
          FROM observations o
          WHERE EXTRACT(MONTH FROM o.from_time) IN (1, 2, 3, 10, 11, 12))
select
    a.*,
    raven_coverage(time,count_valid,t.timestep,'winterseason') as cov,
    now() as created
from (
select
    sampling_point_id,
    date_trunc('year', from_time) as time,
    round(avg(value) FILTER (WHERE validation_flag in (1,2,3)), 10) as val,
    round(min(value) FILTER (WHERE validation_flag in (1,2,3)), 10) as min,
    round(max(value) FILTER (WHERE validation_flag in (1,2,3)), 10) as max,
    count(value)::int AS count_all,
    count(value) FILTER (WHERE validation_flag in (1,2,3))::int AS count_valid,
    count(*) FILTER (WHERE verification_flag = 1)::int as count_verified
from timevalues
group by  sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;

CREATE INDEX idx_obs_winter_season_id_time
on observations_winter_season (sampling_point_id,time);


CREATE UNIQUE INDEX un_obs_winter_season_id_time
on observations_winter_season (sampling_point_id,time);


------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_summer_year;
create materialized view observations_summer_year as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.*,
    raven_coverage(a.time, a.count_valid::int,t.timestep,'summeryear') as cov,
    now() as created
from (
    select
        sampling_point_id,
        date_trunc('year', from_time)                                     as time,
        round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
        round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
        round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
        count(value)          ::int                                            AS count_all,
        count(value) FILTER (WHERE validation_flag >= 1) ::int         AS count_valid,
        count(*) FILTER (WHERE verification_flag = 1)  ::int                   as count_verified
    from observations
    where 1 = 1
    and to_char(from_time, 'MM') IN ('04', '05', '06', '07', '08', '09')
    group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;


CREATE INDEX idx_obs_summer_year_id_time
on observations_summer_year(sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_summer_year_id_time
on observations_summer_year (sampling_point_id,time);


------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_day;
create materialized view observations_day as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.*,
    raven_coverage(time,count_valid,t.timestep, 'day') as cov,
    now() as created
from
(
    select
        sampling_point_id,
        date_trunc('day', from_time) as time,
        round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
        round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
        round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
        count(value)::int AS count_all,
        count(value) FILTER (WHERE validation_flag >= 1) ::int AS count_valid,
        count(*) FILTER (WHERE verification_flag = 1)  ::int as count_verified
      from observations
      group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;

CREATE INDEX idx_obs_day_id_time
on observations_day (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_day_id_time
on observations_day (sampling_point_id,time);



------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_aot40v;
create materialized view observations_aot40v as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.sampling_point_id,
    a.time,
    case when raven_coverage(a.time, a.count_valid,t.timestep,'aot40v') < 100 then round(a.val*count_all/count_valid,10) else a.val  end as val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    raven_coverage(a.time, a.count_valid::int,t.timestep,'aot40v') as cov,
    now() as created
from (
    select
        sampling_point_id,
        date_trunc('year', from_time)                                                             as time,
        round(sum(value - 80) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10) as val,
        round(min(value) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10)      as min,
        round(max(value) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10)      as max,
        count(value)::int                                                                              AS count_all,
        count(value) FILTER (WHERE validation_flag >= 1)::int               AS count_valid,
        count(*) FILTER (WHERE verification_flag = 1)::int                                             as count_verified
    from observations
    where 1 = 1
    and to_char(from_time, 'MM') IN ('05', '06', '07')
    and to_char(from_time, 'HH24') IN ('08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19')
    group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;


CREATE INDEX idx_obs_aot40v_id_time
on observations_aot40v (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_aot40v_id_time
on observations_aot40v (sampling_point_id,time);


------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_aot40f;
create materialized view observations_aot40f as
with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
select
    a.sampling_point_id,
    a.time,
    case when raven_coverage(a.time, a.count_valid,t.timestep,'aot40f') < 100 then round(a.val*count_all/count_valid,10) else a.val  end as val,
    a.min,
    a.max,
    a.count_all,
    a.count_valid,
    a.count_verified,
    raven_coverage(a.time, a.count_valid::int,t.timestep,'aot40f') as cov,
    now() as created
from (
    select
        sampling_point_id,
        date_trunc('year', from_time)                                                             as time,
        round(sum(value - 80) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10) as val,
        round(min(value) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10)      as min,
        round(max(value) FILTER (WHERE validation_flag >= 1 AND value - 80 > 0), 10)      as max,
        count(value)::int                                                                              AS count_all,
        count(value) FILTER (WHERE validation_flag >= 1)::int               AS count_valid,
        count(*) FILTER (WHERE verification_flag = 1)::int                                             as count_verified
    from observations
    where 1 = 1
    and to_char(from_time, 'MM') IN ('04', '05', '06', '07', '08', '09')
    and to_char(from_time, 'HH24') IN ('08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19')
    group by sampling_point_id, time
) a, timeseries t
where a.sampling_point_id = t.sampling_point_id;


CREATE INDEX idx_obs_aot40f_id_time
on observations_aot40f (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_aot40f_id_time
on observations_aot40f (sampling_point_id,time);


------------------------------------------------------------------------------------


DROP MATERIALIZED VIEW IF EXISTS observations_day_8hmax;
CREATE MATERIALIZED VIEW observations_day_8hmax AS
select
    *,
    raven_coverage(time, count_valid::int,timestep,'day') as cov,
    now() as created
from (
    with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
    select
        running_8hours.sampling_point_id,t.timestep,
        date_trunc('day', datetime)  as time,
        max(case when count_valid >= (0.75 * (28800.0 / t.timestep::float)) then val end) as val, -- max is duplicate because it asks for max not avg
        min(case when count_valid >= (0.75 * (28800.0 / t.timestep::float)) then val end) as min,
        max(case when count_valid >= (0.75 * (28800.0 / t.timestep::float)) then val end) as max,
        count(*) as count_all,
        count(case when count_valid >= (0.75 * (28800.0 / t.timestep::float)) then 1 end) as count_valid,
        count(case when count_verified = count_all then 1 else 0 end) as count_verified
      from (
        select
            o.from_time as datetime,
            o.sampling_point_id,
            avg(case when o.validation_flag >= 1 then o.value end)
            over (partition by o.sampling_point_id order by o.from_time range between interval '7 hour' preceding and current row) as val,
            count(*)
            over (partition by o.sampling_point_id order by o.from_time range between interval '7 hour' preceding and current row) as count_all,
            count(case when o.validation_flag >= 1 then 1 end)
            over (partition by o.sampling_point_id order by o.from_time range between interval '7 hour' preceding and current row) as count_valid,
            count(case when o.verification_flag = 1 then 1 end)
            over (partition by o.sampling_point_id order by o.from_time range between interval '7 hour' preceding and current row) as count_verified
        from observations o
      ) as running_8hours, timeseries t
      where running_8hours.sampling_point_id = t.sampling_point_id
      group by running_8hours.sampling_point_id, date_trunc('day', running_8hours.datetime), t.timestep
    ) as running_8hours_max;

CREATE INDEX idx_obs_day_8hmax_id_time
  ON observations_day_8hmax (sampling_point_id, time);

CREATE UNIQUE INDEX un_obs_day_8hmax_id_time
  ON observations_day_8hmax (sampling_point_id, time);

------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_year_hour;
create materialized view observations_year_hour as
select
    *,
    raven_coverage(time, count_valid::int,timestep,'year') as cov,
    now() as created
from (
    with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
    select
        hourly.sampling_point_id,t.timestep,
        date_trunc('year', datetime)  as time,
        avg(case when count_valid >= (0.75 * (3600.0 / t.timestep::float)) then val end) as val,
        min(case when count_valid >= (0.75 * (3600.0 / t.timestep::float)) then val end) as min,
        max(case when count_valid >= (0.75 * (3600.0 / t.timestep::float)) then val end) as max,
        count(*) as count_all,
        count(case when count_valid >= (0.75 * (3600.0 / t.timestep::float)) then 1 end) as count_valid,
        count(case when count_verified = count_all then 1 else 0 end) as count_verified
      from (
        select
            sampling_point_id,
            date_trunc('hour', from_time) as datetime,
            round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
            round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
            round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
            count(value)::int AS count_all,
            count(value) FILTER (WHERE validation_flag >= 1) ::int AS count_valid,
            count(*) FILTER (WHERE verification_flag = 1)  ::int as count_verified
          from observations
          group by sampling_point_id, datetime
      ) as hourly, timeseries t
      where hourly.sampling_point_id = t.sampling_point_id
      group by hourly.sampling_point_id, date_trunc('year', hourly.datetime), t.timestep
    ) as yearly;


CREATE INDEX idx_obs_year_hour_id_time
on observations_year_hour (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_year_hour_id_time
on observations_year_hour (sampling_point_id,time);

------------------------------------------------------------------------------------

DROP MATERIALIZED VIEW IF EXISTS observations_year_day;
create materialized view observations_year_day as
select
    *,
    raven_coverage(time, count_valid::int,timestep,'year') as cov,
    now() as created
from (
    with timeseries as (select s.id as sampling_point_id, t.timestep from sampling_points s, eea_times t WHERE s.timestep = t.id)
    select
        daily.sampling_point_id,t.timestep,
        date_trunc('year', datetime)  as time,
        avg(case when count_valid >= (0.75 * (86400.0 / t.timestep::float)) then val end) as val,
        min(case when count_valid >= (0.75 * (86400.0 / t.timestep::float)) then val end) as min,
        max(case when count_valid >= (0.75 * (86400.0 / t.timestep::float)) then val end) as max,
        percentile_cont(0.99) WITHIN GROUP (ORDER BY case when count_valid >= (0.75 * (86400.0 / t.timestep::float)) then val end)::numeric as p99,
        count(*) as count_all,
        count(case when count_valid >= (0.75 * (86400.0 / t.timestep::float)) then 1 end) as count_valid,
        count(case when count_verified = count_all then 1 else 0 end) as count_verified
      from (
        select
            sampling_point_id,
            date_trunc('day', from_time) as datetime,
            round(avg(value) FILTER (WHERE validation_flag >= 1), 10) as val,
            round(min(value) FILTER (WHERE validation_flag >= 1), 10) as min,
            round(max(value) FILTER (WHERE validation_flag >= 1), 10) as max,
            count(value)::int AS count_all,
            count(value) FILTER (WHERE validation_flag >= 1) ::int AS count_valid,
            count(*) FILTER (WHERE verification_flag = 1)  ::int as count_verified
          from observations
          group by sampling_point_id, datetime
      ) as daily, timeseries t
      where daily.sampling_point_id = t.sampling_point_id
      group by daily.sampling_point_id, date_trunc('year', daily.datetime), t.timestep
    ) as yearly;


CREATE INDEX idx_obs_year_day_id_time
on observations_year_day (sampling_point_id,time);

CREATE UNIQUE INDEX un_obs_day_hour_id_time
on observations_year_day (sampling_point_id,time);