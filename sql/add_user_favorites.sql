-- Migration: add user_favorites table
-- Per-user named favorites storing a dashboard plot configuration as JSONB.
-- config = { title, timePreset, plotType, fullWidth, seriesIds: [int...] }
-- Used by the Dashboard (save/restore plots) and as quick sampling point
-- selections in Historical, Verify and Validate.

create table if not exists user_favorites (
    id      serial primary key,
    user_id integer      not null references users (id) on delete cascade,
    name    varchar(255) not null,
    config  jsonb        not null default '{}',
    created timestamp    default now(),
    updated timestamp,
    unique (user_id, name)
);
