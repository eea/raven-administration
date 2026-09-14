-- ===========================================================================
-- 024 — an assessment method may be a model, and a regime link may have a period
--
-- `assessmentdata` is the junction between an assessment regime and the methods
-- assessing it. It is what core/data/plans_programs_export.py walks to derive
-- ComplianceAssessmentMethod, so it decides what Raven can report at all. Two
-- things it could not express:
--
-- A MODEL CANNOT BE AN ASSESSMENT METHOD. AQR3 CAM_05 AssessmentMethodId is
-- "either a sampling_points.id (measurement) or a models.id (model/OBE)" --
-- schema.sql says so, the CAM management grid resolves the column against both
-- tables, and ADJ_04 and SRS_06 follow the same convention. This table's own
-- column comment said 'Sampling point ID or model ID' too. But the column carried
--
--     assessmentlocal_id varchar(100) not null references sampling_points
--
-- so a MOD_/OBE_ id could not physically be stored, and a zone assessed by
-- modelling reported no compliance whatever. The same contradiction was in v3.
--
-- The fix keeps the referential integrity the foreign key was giving. Two nullable
-- foreign keys, one per kind, both still cascading on delete -- so removing a
-- sampling point or a model still takes its links with it, which a validating
-- trigger could not do -- and `assessmentlocal_id` becomes a generated column over
-- the two. That last part is what makes this cheap: every reader keeps working
-- unchanged, and there is exactly one writer to adjust (sql/raven4_migrate/
-- migrate_v3_to_v4.py, changed in the same commit; a generated column rejects an
-- explicit INSERT).
--
-- A LINK HAS NO PERIOD. Recalculating an earlier reporting year used today's
-- regime links rather than the ones valid in that year, so an earlier submission
-- could not be reproduced. `sampling_points` has carried from_time/to_time all
-- along and the derivation already bounds the year by them; this gives the link
-- the same two columns and the same NULL-permissive reading.
--
-- THE FIRST EXPORT AFTER THIS MIGRATION IS UNCHANGED. There is deliberately no
-- backfill: both bounds start NULL, which the derivation treats as unbounded, so
-- every existing link still matches every year. Nothing is inferred from
-- assessment_regimes.classification_year either -- ARZ_18 is when the zone
-- classification was made and is a component of ARZ_02, not a validity window. A
-- regime classified in 2022 is still the applicable regime in 2024, and
-- backfilling from it would silently stop old regimes producing rows.
--
-- WHAT HAS NEVER BEEN TRUE AND NOW IS. Nothing stopped two identical links
-- between one regime and one method. Each duplicate produces a duplicate CAM
-- primary key, which the upsert collapses arbitrarily. With a management screen
-- for this table -- added in the same release, there was none before -- that stops
-- being a theoretical risk, so the pair is made unique per period. NULLs are
-- distinct in a plain unique index and UNIQUE NULLS NOT DISTINCT needs PG15, so
-- the index coalesces the lower bound instead.
--
-- Idempotent; a no-op on a fresh install, where schema.sql already declares all of
-- it and seeds this version.
-- ===========================================================================

begin;

alter table assessmentdata
    add column if not exists sampling_point_id varchar(100),
    add column if not exists model_id          varchar(100),
    add column if not exists from_time         timestamp,
    add column if not exists to_time           timestamp;

-- Every existing row is a sampling point: that is what the old foreign key
-- guaranteed. Guarded so a re-run cannot overwrite a link since pointed at a model.
do $$
begin
    if not exists (select 1 from schema_version where version = '4.502.24') then
        update assessmentdata
           set sampling_point_id = assessmentlocal_id
         where sampling_point_id is null
           and model_id is null;
        raise notice '024: % existing link(s) recorded as sampling points',
            (select count(*) from assessmentdata where sampling_point_id is not null);
    end if;
end $$;

-- Drop the old foreign key by discovery rather than by name: migration 008 renamed
-- the column but left constraint names carrying the pre-rename spelling, so the
-- generated name cannot be assumed.
do $$
declare
    constraint_name text;
begin
    select conname into constraint_name
      from pg_constraint
     where conrelid = 'assessmentdata'::regclass
       and contype = 'f'
       and pg_get_constraintdef(oid) like '%assessmentlocal_id%'
       and pg_get_constraintdef(oid) like '%sampling_points%';
    if constraint_name is not null then
        execute format('alter table assessmentdata drop constraint %I', constraint_name);
        raise notice '024: dropped %, which pinned assessmentlocal_id to sampling_points',
            constraint_name;
    end if;
end $$;

do $$
begin
    if not exists (select 1 from pg_constraint
                    where conname = 'assessmentdata_sampling_point_fkey') then
        alter table assessmentdata
            add constraint assessmentdata_sampling_point_fkey
            foreign key (sampling_point_id) references sampling_points
            on update cascade on delete cascade;
    end if;
    if not exists (select 1 from pg_constraint
                    where conname = 'assessmentdata_model_fkey') then
        alter table assessmentdata
            add constraint assessmentdata_model_fkey
            foreign key (model_id) references models
            on update cascade on delete cascade;
    end if;
    if not exists (select 1 from pg_constraint
                    where conname = 'assessmentdata_one_method') then
        alter table assessmentdata
            add constraint assessmentdata_one_method
            check (num_nonnulls(sampling_point_id, model_id) = 1);
    end if;
    if not exists (select 1 from pg_constraint
                    where conname = 'assessmentdata_period_ordered') then
        alter table assessmentdata
            add constraint assessmentdata_period_ordered
            check (to_time is null or from_time is null or to_time > from_time);
    end if;
end $$;

-- assessmentlocal_id becomes derived. Guarded on the column not already being
-- generated, so a re-run cannot drop a populated column.
do $$
begin
    if exists (select 1 from information_schema.columns
                where table_name = 'assessmentdata'
                  and column_name = 'assessmentlocal_id'
                  and is_generated = 'NEVER') then
        alter table assessmentdata drop column assessmentlocal_id;
        alter table assessmentdata
            add column assessmentlocal_id varchar(100)
            generated always as (coalesce(sampling_point_id, model_id)) stored;
        raise notice '024: assessmentlocal_id is now generated from sampling_point_id / model_id';
    end if;
end $$;

-- One link per regime, method and period. Coalesced because NULLs are distinct in a
-- plain unique index and UNIQUE NULLS NOT DISTINCT needs PG15.
create unique index if not exists assessmentdata_regime_method_period_uq
    on assessmentdata (assessment_regime_id, assessmentlocal_id,
                       coalesce(from_time, '-infinity'::timestamp));

comment on column assessmentdata.sampling_point_id is
    'AQR3 CAM_05 when the regime is assessed by measurement. Exactly one of this and '
    'model_id is set; assessmentlocal_id is generated from the pair.';
comment on column assessmentdata.model_id is
    'AQR3 CAM_05 when the regime is assessed by a model or objective estimation '
    '(models.id, MOD_ or OBE_). Exactly one of this and sampling_point_id is set.';
comment on column assessmentdata.assessmentlocal_id is
    'AQR3 CAM_05 AssessmentMethodId, generated from sampling_point_id / model_id so '
    'every reader sees one column regardless of which kind of method it is.';
comment on column assessmentdata.from_time is
    'When this method started assessing this regime. NULL means unbounded, so a link '
    'that predates 4.502.24 still matches every reporting year and the first export '
    'after that migration is unchanged. Deliberately NOT derived from '
    'assessment_regimes.classification_year, which is when the zone classification was '
    'made rather than a validity window.';
comment on column assessmentdata.to_time is
    'When this method stopped assessing this regime. NULL means still current. Close a '
    'link rather than deleting it, so recalculating an earlier reporting year still '
    'reproduces what was submitted for it.';

insert into schema_version (version, description)
values ('4.502.24',
        'assessmentdata links a regime to either a sampling point or a model, and '
        'carries a validity period. CAM_05 is documented as spanning sampling_points '
        'and models, but the column was foreign-keyed to sampling_points alone, so a '
        'zone assessed by modelling could report no compliance at all; and the link had '
        'no period, so recalculating an earlier year used today''s links rather than '
        'the ones valid then. assessmentlocal_id becomes a generated column over the '
        'two new foreign keys, so every reader is unaffected. No backfill: both period '
        'bounds start NULL, which reads as unbounded, so the first export after this '
        'migration is unchanged')
on conflict (version) do nothing;

commit;
