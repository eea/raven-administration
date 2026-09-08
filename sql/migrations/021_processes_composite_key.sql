-- ===========================================================================
-- 021 — processes keys on the AQR3 SPP key, not on ProcessId alone
--
-- AQR3 v5.02 marks four SPP attributes as primary key: SPP_01 CountryCode,
-- SPP_02 ProcessId, SPP_03 AssessmentMethodId and SPP_04 ProcessActivityBegin.
-- CountryCode is instance-wide (settings.country_code_id) rather than a column
-- here, so the remaining three are the key.
--
-- The guide is explicit that ProcessId is not on its own an identity. SPP_02's
-- own remark:
--
--     "The same ProcessId can be re-used for the same equipment configurations
--      under different sampling points (AssessmentMethodId)."
--
-- That is the point of the attribute: one equipment configuration, named once,
-- applied to every sampling point it serves. `processes` declared its primary
-- key on `id` alone, so a configuration could be attached to exactly one
-- sampling point and the second use had to be given a made-up different id --
-- at which point the two are no longer recognisably the same configuration in
-- the submission.
--
-- ProcessActivityBegin is in the key for the other half of the same idea: SPP_04
-- lets one sampling point carry the same ProcessId over several distinct
-- operating periods, which is how an instrument that is removed and later
-- reinstalled is reported. Under the old key the second period overwrote the
-- first.
--
-- The SPP export already ordered by the real key -- ORDER BY p.id,
-- p.process_activity_begin in core/reporting/aqr3/spec.py -- so the narrow
-- primary key was an oversight rather than a decision.
--
-- WHY THIS CANNOT LOSE DATA. Widening a key only ever admits rows; it cannot
-- reject any. A primary key on `id` alone already makes (id, sampling_point_id,
-- process_activity_begin) unique, so the new constraint is satisfied by
-- construction. Both key columns being added are already NOT NULL, so unlike
-- migration 018 there is nothing to tighten and no row that cannot be placed.
-- The duplicate check below is therefore an invariant assertion, not a live
-- risk -- kept because the constraint is discovered rather than assumed, and a
-- database whose key is something else entirely could hold duplicates.
--
-- Nothing references `processes`: it has no inbound foreign keys anywhere in
-- schema.sql, so there is no dependent constraint to drop and recreate. The four
-- "latest process per sampling point" queries in core/query.py, core/data/mean.py
-- and the dashboard and latest endpoints all key on sampling_point_id and order by
-- process_activity_begin, so a repeated `id` does not disturb them.
--
-- Idempotent, and a no-op on a fresh install -- schema.sql declares the composite
-- key in the same commit, so this recognises it and skips.
-- ===========================================================================

begin;

do $$
declare
    -- Declared order matters only for the backing index; it is compared exactly so
    -- that a database already carrying this key is left completely alone. `id`
    -- leads so that a lookup by ProcessId alone still uses the primary key index.
    TARGET_KEY constant text[] := array['id', 'sampling_point_id', 'process_activity_begin'];
    pk    record;
    dupes bigint;
begin
    if to_regclass('public.processes') is null then
        raise exception
            '021: there is no `processes` table. sql/schema.sql creates it in every '
            'install, so this database is not a Raven schema.';
    end if;

    select con.conname::text as conname,
           (select array_agg(att.attname::text order by k.ord)
              from unnest(con.conkey) with ordinality as k(attnum, ord)
              join pg_attribute att on att.attrelid = con.conrelid
                                   and att.attnum   = k.attnum) as cols
      into pk
      from pg_constraint con
     where con.contype = 'p'
       and con.conrelid = to_regclass('public.processes');

    if pk.conname is null then
        raise exception
            '021: `processes` has no primary key at all, so there is nothing to '
            'replace and the table is not the one schema.sql describes. Investigate '
            'before re-running.';
    end if;

    if pk.cols = TARGET_KEY then
        raise notice '021: processes already keys on (%) -- nothing to do',
            array_to_string(pk.cols, ', ');
    else
        raise notice '021: processes keys on (%) via %; widening to the AQR3 SPP key',
            array_to_string(pk.cols, ', '), pk.conname;

        -- Unreachable from the key this migration expects to find, for the reason in
        -- the header. Checked anyway because the constraint is discovered, not
        -- assumed: adding the primary key over duplicates would fail with Postgres's
        -- own message naming one row rather than the whole problem.
        select count(*) into dupes
          from (select 1 from processes
                 group by id, sampling_point_id, process_activity_begin
                having count(*) > 1) d;
        if dupes > 0 then
            raise exception
                '021: % (id, sampling_point_id, process_activity_begin) triple(s) '
                'appear more than once in processes, so they cannot all become primary '
                'keys. Inspect with: SELECT id, sampling_point_id, '
                'process_activity_begin, count(*) FROM processes GROUP BY 1, 2, 3 '
                'HAVING count(*) > 1;', dupes;
        end if;

        execute format('alter table processes drop constraint %I', pk.conname);
        alter table processes
            add primary key (id, sampling_point_id, process_activity_begin);
        raise notice '021: processes now keys on (id, sampling_point_id, '
                     'process_activity_begin)';
    end if;
end $$;

-- Restated because the meaning of `id` changed: it names an equipment
-- configuration now, not a row.
comment on column processes.id is
    'AQR3 SPP_02 ProcessId. One third of the primary key: the same ProcessId is '
    're-used for the same equipment configuration under different sampling points';
comment on column processes.sampling_point_id is
    'AQR3 SPP_03 AssessmentMethodId -> sampling_points. Part of the primary key, and '
    'the SPP export inner joins it -- a process without one is not reported at all';
comment on column processes.process_activity_begin is
    'AQR3 SPP_04 ProcessActivityBegin. Part of the primary key: one sampling point may '
    'carry the same ProcessId over several distinct operating periods';

comment on table processes is
    'v4.502 AQR3 SamplingProcess (SPP). Keyed on (ProcessId, AssessmentMethodId, '
    'ProcessActivityBegin) as AQR3 specifies; CountryCode, the fourth key attribute, '
    'is instance-wide and comes from settings.country_code_id';

insert into schema_version (version, description)
values ('4.502.21',
        'processes keys on (id, sampling_point_id, process_activity_begin) rather than '
        'id alone. AQR3 marks ProcessId, AssessmentMethodId and ProcessActivityBegin '
        'all as primary key, and SPP_02 states that the same ProcessId is re-used for '
        'the same equipment configuration under different sampling points; the old key '
        'allowed each configuration exactly one sampling point and one operating '
        'period. Widening only admits rows, so no existing data can be rejected')
on conflict (version) do nothing;

commit;
