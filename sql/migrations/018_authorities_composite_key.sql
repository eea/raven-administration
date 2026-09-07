-- ===========================================================================
-- 018 — authorities keys on the AQR3 AUT key, not on AuthorityInstanceId alone
--
-- AQR3 v5.02 marks four AUT attributes as primary key: AUT_01 CountryCode,
-- AUT_02 AuthorityInstanceId, AUT_03 AuthorityRole and AUT_04 Email. Role and
-- email are in the key on purpose -- one authority instance is meant to carry
-- several authorities, and the reporting guide's own Authority example sheet does
-- exactly that, two rows on the same country/instance separated only by role and
-- email:
--
--     DU | DU | 1 | eve.bot@dema.dus  | nuts0 | Dustovia Environmental Agency
--     DU | DU | 2 | adam.bot@dema.dus | nuts0 | Dustovia Environmental Agency
--
-- `authorities` declared its primary key on `id` alone, so it could hold one row
-- per AuthorityInstanceId and the shape above was unrepresentable. CountryCode is
-- instance-wide (settings.country_code_id) rather than a column here, so the
-- remaining three are the key.
--
-- Measured on Norway, which is what surfaced this: seven national competent-
-- authority roles across two organisations -- Miljodirektoratet reporting and
-- analysing, NILU's national reference laboratory assessing, approving measurement
-- systems, ensuring accuracy and running the QA programme. Under the old key
-- exactly one of them could be stored, and the reference laboratory would simply
-- not appear in the submission.
--
-- The AUT export already sorted by the real key -- ORDER BY a.id, ar.notation,
-- a.email in core/reporting/aqr3/spec.py -- so the single-column primary key was
-- an oversight rather than a decision.
--
-- WHY THIS REFUSES RATHER THAN REPAIRS. A widened key can only fail on data that
-- is already ambiguous: a row with no AuthorityRole, since the column was nullable
-- and is about to join the key. Those are operator-entered contact details, and
-- picking a winner would discard someone's address or phone number silently, so they
-- are counted and the migration aborts naming the query to run. (A duplicate
-- (id, role, email) triple is checked too, but cannot occur while the key being
-- replaced is `id` alone -- that already makes the triple unique. It guards the case
-- where the discovered key is something else.)
--
-- Nothing references `authorities` -- it has no inbound foreign keys anywhere in
-- schema.sql -- so unlike migrations 016 and 017 there is nothing to repoint and no
-- cascade to fear; the only data at risk is the table's own.
--
-- The primary key is discovered from pg_constraint rather than named, the way
-- migration 004 finds the foreign key it has to drop: `authorities_pkey` is only
-- the name PostgreSQL happens to generate for an inline `primary key`, and a
-- database built by some other route may not use it.
--
-- Idempotent, and a no-op on a fresh install -- schema.sql declares the composite
-- key in the same commit, so this recognises it and skips.
-- ===========================================================================

begin;

do $$
declare
    -- Declared order matters only for the backing index; it is compared exactly so
    -- that a database already carrying this key is left completely alone.
    TARGET_KEY constant text[] := array['id', 'authority_role_id', 'email'];
    pk          record;
    nulls       bigint;
    dupes       bigint;
begin
    if to_regclass('public.authorities') is null then
        raise exception
            '018: there is no `authorities` table. sql/schema.sql creates it in every '
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
       and con.conrelid = to_regclass('public.authorities');

    if pk.conname is null then
        raise exception
            '018: `authorities` has no primary key at all, so there is nothing to '
            'replace and the table is not the one schema.sql describes. Investigate '
            'before re-running.';
    end if;

    if pk.cols = TARGET_KEY then
        raise notice '018: authorities already keys on (%) -- nothing to do',
            array_to_string(pk.cols, ', ');
    else
        raise notice '018: authorities keys on (%) via %; widening to the AQR3 AUT key',
            array_to_string(pk.cols, ', '), pk.conname;

        -- Guard 1. authority_role_id was nullable and is about to become part of the
        -- key. A NULL role is not a row this migration can place.
        select count(*) into nulls
          from authorities where authority_role_id is null;
        if nulls > 0 then
            raise exception
                '018: % authorities row(s) have no authority_role_id, which the AQR3 '
                'key requires (AUT_03). Assign each one a role from '
                'eea_authorityobject -- "reporting" or "assessment" -- then re-run. '
                'Inspect with: SELECT id, email, authority_name FROM authorities '
                'WHERE authority_role_id IS NULL;', nulls;
        end if;

        -- Guard 2. Two rows collapsing onto one key triple. Unreachable from the key
        -- this migration expects to find -- a primary key on `id` alone already makes
        -- the triple unique, as does any key that is a subset of it -- so this is an
        -- invariant check rather than a live risk. It is kept because the constraint is
        -- discovered rather than assumed: a database whose key is something else
        -- entirely can hold duplicates, and adding the primary key would then fail with
        -- Postgres's own message naming one row instead of the whole problem.
        select count(*) into dupes
          from (select 1 from authorities
                 group by id, authority_role_id, email
                having count(*) > 1) d;
        if dupes > 0 then
            raise exception
                '018: % (id, authority_role_id, email) triple(s) appear more than once '
                'in authorities, so they cannot all become primary keys. These are '
                'operator-entered contacts and this migration will not choose between '
                'them. Inspect with: SELECT id, authority_role_id, email, count(*) '
                'FROM authorities GROUP BY 1, 2, 3 HAVING count(*) > 1;', dupes;
        end if;

        if exists (select 1 from information_schema.columns
                    where table_schema = 'public'
                      and table_name   = 'authorities'
                      and column_name  = 'authority_role_id'
                      and is_nullable  = 'YES')
        then
            alter table authorities alter column authority_role_id set not null;
            raise notice '018: authorities.authority_role_id set NOT NULL (AUT_03 is '
                         'part of the key)';
        end if;

        execute format('alter table authorities drop constraint %I', pk.conname);
        alter table authorities add primary key (id, authority_role_id, email);
        raise notice '018: authorities now keys on (id, authority_role_id, email)';
    end if;
end $$;

-- Restated because the meaning of `id` changed: it is one third of the key now, not
-- the identity of the row.
comment on column authorities.id is
    'AQR3 AUT_02 AuthorityInstanceId. One third of the primary key: several '
    'authorities may share an instance, differing by role and email';
comment on column authorities.authority_role_id is
    'AQR3 AUT_03 AuthorityRole -> eea_authorityobject. Part of the primary key';
comment on column authorities.email is
    'AQR3 AUT_04 Email. Part of the primary key -- it is what separates two '
    'organisations holding the same role for the same instance';

comment on table authorities is
    'Reportnet3 authority contacts, feeding AQR3 AUT. Keyed on (AuthorityInstanceId, '
    'AuthorityRole, Email) as AQR3 specifies; CountryCode, the fourth key attribute, '
    'is instance-wide and comes from settings.country_code_id';

insert into schema_version (version, description)
values ('4.502.18',
        'authorities keys on (id, authority_role_id, email) rather than id alone. AQR3 '
        'marks AuthorityInstanceId, AuthorityRole and Email all as primary key so one '
        'instance can carry several authorities, which is how a country reports both a '
        'reporting authority and a separate reference laboratory; the old key could '
        'store exactly one row per instance. authority_role_id becomes NOT NULL, and a '
        'row with no role or a duplicate triple aborts the migration rather than being '
        'silently picked between')
on conflict (version) do nothing;

commit;
