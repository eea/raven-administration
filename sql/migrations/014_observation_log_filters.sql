-- ===========================================================================
-- 014 — observation log filter rules and per-user history preferences
--
-- The AirQUIS import made the change history useful and simultaneously unreadable:
-- a single sampling point now carries up to 136,192 log rows, the overwhelming
-- majority written by ADACS imports and by the migration itself. What an operator
-- wants to see is the manual QC decisions, not the machine traffic around them.
--
-- Two stores, because they answer two different questions.
--
-- settings.observation_log_config  — what this instance considers noise. Authored by
--   an administrator (the endpoint requires management + allnetworks) and shared by
--   everyone. Shape:
--     { "hidden_columns": ["changed_by"],
--       "rules": [ { "id": "r1a7f", "label": "ADACS imports", "action": "hide",
--                    "enabled_by_default": true, "match": "all",
--                    "conditions": [ {"field":"change_source","op":"eq",
--                                     "value":"adacs_import"} ] } ] }
--   Rule ids are stable slugs, not array positions: user_log_preferences references
--   them, so reordering or relabelling a rule must not silently re-enable it.
--
-- user_log_preferences — each user's *deviation* from that default, never a snapshot
--   of it. Storing only the deviation is what lets an administrator change the house
--   rules and have every user pick the change up. Shape:
--     { "disabled_rule_ids": ["r1a7f"], "hidden_columns": ["period_to"] }
--   A dangling disabled_rule_id (admin deleted the rule) is harmless and ignored.
--
-- Per-user rather than browser-local so the setting follows a user between machines.
-- Modelled on user_favorites, the only other per-user store: user_id FK with
-- ON DELETE CASCADE, JSONB config, and endpoints that scope by the JWT username
-- rather than trusting a client-supplied id. One row per user, hence user_id as the
-- primary key rather than a serial plus a unique constraint.
--
-- Idempotent.
-- ===========================================================================

begin;

alter table settings
    add column if not exists observation_log_config jsonb not null default '{}'::jsonb;

comment on column settings.observation_log_config is
    'Instance-wide Observation Change History configuration: { hidden_columns: [...], '
    'rules: [...] }. Rules are filter definitions with stable string ids, applied in SQL '
    'by api/core/observation_log_filters.py. Empty object means no filtering.';

create table if not exists user_log_preferences
(
    user_id integer primary key
        references users
            on delete cascade,
    config  jsonb     not null default '{}',
    updated timestamp default now()
);

comment on table user_log_preferences is
    'Per-user deviations from settings.observation_log_config for the Observation Change '
    'History: { disabled_rule_ids: [...], hidden_columns: [...] }. Stores only the '
    'departure from the instance default, so administrator changes propagate.';

insert into schema_version (version, description)
values ('4.502.14',
        'Observation Change History filtering: settings.observation_log_config holds the '
        'instance-wide column and filter-rule defaults, user_log_preferences holds each '
        'user''s deviation from them (disabled rule ids, hidden columns). Rules are '
        'evaluated in SQL so LIMIT counts visible rows and pagination stays exact')
on conflict (version) do nothing;

commit;
