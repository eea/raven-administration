-- ===========================================================================
-- 035 — "importing" group permission
--
-- Importing observations (Manual import, /api/imports/observations and the logger
-- API) used to require the management permission, which also allows editing
-- stations, sampling points and other metadata. A group with importing (and all
-- networks) can now import without it. Management still includes importing, so
-- existing groups keep working and nothing is backfilled.
--
-- Idempotent. On a fresh install schema.sql declares the column and records this
-- migration as applied.
-- ===========================================================================

begin;

alter table "group" add column if not exists importing boolean not null default false;

insert into schema_version (version, description)
values ('4.502.35', 'group.importing: import observations without the management permission')
on conflict (version) do nothing;

commit;
