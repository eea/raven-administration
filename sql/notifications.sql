-- Create function first (needed for trigger)
create or replace function raven_limit_notification_runs() returns trigger
    language plpgsql
as
$$
BEGIN
    -- Keep only the latest 100 rows
    DELETE FROM notifications_runs
    WHERE id NOT IN (
        SELECT id FROM notifications_runs
        ORDER BY run_timestamp DESC
        LIMIT 100
    );
    RETURN NEW;
END;
$$;

-- Create sequence for notifications_runs
create sequence if not exists notification_runs_id_seq
    as integer;

-- Create notifications table
create table if not exists notifications
(
    name    text                 not null constraint notifications_pk primary key,
    emails  text                 not null,
    enabled boolean default true not null
);

-- Create notifications_runs table
create table if not exists notifications_runs
(
    id                   integer                  default nextval('notification_runs_id_seq'::regclass) not null
        primary key,
    run_timestamp        timestamp with time zone default now()                                         not null,
    missing_data_count   integer                                                                        not null,
    notifications_sent   integer                                                                        not null,
    notifications_failed integer                                                                        not null,
    smtp_server          text,
    execution_time_ms    integer,
    status               text                                                                           not null,
    error_message        text,
    details              jsonb
);

-- Set sequence ownership
alter sequence notification_runs_id_seq owned by notifications_runs.id;

-- Create notifications_samplingpoints table (depends on notifications table)
create table if not exists notifications_samplingpoints
(
    notification_id   text         not null
        constraint notifications_samplingpoints_notifications_name_fk
            references notifications
            on update cascade on delete cascade,
    sampling_point_id varchar(100) not null
        constraint notifications_samplingpoints_sampling_points_id_fk
            references sampling_points
            on update cascade on delete cascade,
    constraint notifications_samplingpoints_pk
        primary key (sampling_point_id, notification_id)
);

-- Create indexes
create index if not exists idx_notifications_runs_timestamp
    on notifications_runs (run_timestamp);

create index if not exists idx_notifications_runs_status
    on notifications_runs (status);

-- Create trigger (depends on function and table)
drop trigger if exists limit_notification_runs_trigger on notifications_runs;
create trigger limit_notification_runs_trigger
    after insert
    on notifications_runs
    for each row
execute procedure raven_limit_notification_runs();