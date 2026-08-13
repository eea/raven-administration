-- ===========================================================================
-- 008 — Rename assessmentregime_id -> assessment_regime_id
--
-- sql/schema.sql declares `assessment_regime_id` on both assessmentdata and
-- attainments, but databases created before v4 carry the v3 spelling
-- `assessmentregime_id`. Same drift class as `settings` in 006 and
-- `timezone_offset` in 007: schema.sql uses `create table if not exists`, which
-- is a no-op on an existing table, so an in-place edit never reached deployed
-- databases.
--
-- The intended direction is not a guess — the repo's own v3->v4 migrator
-- sql/raven4_migrate/migrate_v3_to_v4.py:1049-1054 reads the source column
-- `assessmentregime_id` and writes it into the target column
-- `assessment_regime_id`. Databases that never went through that path kept the
-- old name.
--
-- Symptom: "Recalculate compliance" on Dataflow Export 500s with
--     column ad.assessment_regime_id does not exist
--     Perhaps you meant to reference the column "ad.assessmentregime_id".
-- from core/data/plans_programs_export.py::_query_exceedances, which is the
-- source for the AQR3 ComplianceAssessmentMethod (CAM) table.
--
-- PostgreSQL rewrites dependent foreign keys and indexes automatically. Their
-- *names* keep the old string (assessmentdata_assessmentregime_id_fkey); that is
-- cosmetic, and renaming constraints as well would add failure modes for no
-- benefit, so they are deliberately left alone.
--
-- Idempotent, and a no-op on a database already in the v4 shape.
-- ===========================================================================

begin;

do
$$
    declare
        t        text;
        has_old  boolean;
        has_new  boolean;
        n        bigint;
    begin
        foreach t in array array['assessmentdata', 'attainments']
            loop
                if to_regclass('public.' || t) is null then
                    raise warning '% does not exist — skipping', t;
                    continue;
                end if;

                select
                    count(*) filter (where column_name = 'assessmentregime_id') > 0,
                    count(*) filter (where column_name = 'assessment_regime_id') > 0
                into has_old, has_new
                from information_schema.columns
                where table_schema = 'public' and table_name = t;

                if has_old and has_new then
                    -- Both spellings present. Which one the data lives in is not
                    -- knowable here, and picking wrong would silently orphan every
                    -- row's regime link. Fail loudly and let a human decide.
                    raise exception
                        '% has BOTH assessmentregime_id and assessment_regime_id. Cannot rename '
                        'automatically — inspect the two columns, consolidate them by hand, drop '
                        'the redundant one, then re-run this migration.', t;

                elsif has_old then
                    execute format(
                        'alter table %I rename column assessmentregime_id to assessment_regime_id', t);
                    execute format('select count(*) from %I', t) into n;
                    raise notice
                        '%.assessmentregime_id renamed to assessment_regime_id (% row(s) carried over)',
                        t, n;

                elsif has_new then
                    raise notice '%.assessment_regime_id already correct — nothing to do', t;

                else
                    raise warning
                        '% has neither assessmentregime_id nor assessment_regime_id. This is not a '
                        'shape any version of raven expects — compliance and attainment generation '
                        'will not work against it.', t;
                end if;
            end loop;
    end
$$;

comment on column assessmentdata.assessment_regime_id is 'FK to assessment_regimes. Read by the AQR3 CAM export via core/data/plans_programs_export.py.';
comment on column attainments.assessment_regime_id is 'FK to assessment_regimes. Read by the XML dataflow G export only; the AQR3 CSVs derive AttainmentId instead.';

insert into schema_version (version, description)
values ('4.502.8',
        'Rename assessmentdata/attainments.assessmentregime_id to assessment_regime_id to match '
        'schema.sql (fixes the 500 on Recalculate compliance)')
on conflict (version) do nothing;

commit;
