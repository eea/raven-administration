-- ===========================================================================
-- 005 — Daily check log (sampling point log)
--
-- Backfills the migration path for the daily check feature, which shipped in
-- schema.sql only:
--
--   sampling_points.daily_check   enables the per-series checkbox in the
--                                 dashboard plot legend
--   sampling_point_log            manual narrative + daily check log per
--                                 sampling point (Oracle AQTL_TIMESERIESLOG)
--
-- Raven-internal, no AQR3 equivalent. Existing databases never received either
-- object, so /api/management/samplingpoints/log/* and the dashboard sampling
-- point query fail there until this runs.
--
-- Idempotent: safe to re-run.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- 1. New column: daily check enabled
-- ---------------------------------------------------------------------------

alter table sampling_points
    add column if not exists daily_check boolean default false not null;

comment on column sampling_points.daily_check is 'Raven-internal: when true, the daily check feature is enabled (shows checkbox in dashboard). No AQR3 equivalent.';

-- ---------------------------------------------------------------------------
-- 2. Sampling point log (manual narrative log per sampling point)
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

-- One daily check per sampling point per calendar day. The insert endpoint
-- relies on this index for its ON CONFLICT ... DO NOTHING guard.
create unique index if not exists uq_spl_daily_check_per_day
    on sampling_point_log (sampling_point_id, created_date)
    where type = 'daily_check';

insert into schema_version (version, description)
values ('5.0.0-dailycheck',
        'Raven-internal: add sampling_points.daily_check and sampling_point_log (daily check / manual log per sampling point)')
on conflict (version) do nothing;

commit;
