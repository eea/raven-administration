-- ===========================================================================
-- 006 — Bring `settings` forward from the v3 shape
--
-- schema.sql declares settings with `create table if not exists`, which is a
-- no-op on a database that already has the table. The v3 -> v4 column swap was
-- an in-place rewrite of schema.sql with no companion ALTER TABLE, and no
-- migration has ever touched settings — so every database created before v4
-- still has:
--
--     id                 serial       not null primary key,
--     namespace          varchar(255) not null unique,
--     uom_m              varchar(255) not null,
--     observation_prefix varchar(10)  not null,
--     language_code      varchar(3)   not null
--     -- some variants also: country, country_code (NOT NULL but WITH defaults)
--
-- while the application expects (country_code_id, timezone_id).
--
-- Symptom: saving Settings 500s with
--     column "country_code_id" of relation "settings" does not exist
-- but the wider damage is that core/reporting/aqr3/context.py and
-- core/data/processing/common.py also read those columns, so every AQR3 export
-- and observation import fails on the old shape too.
--
-- Idempotent, and a harmless no-op on a database already in the v4 shape.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- 1. The v4 columns
-- ---------------------------------------------------------------------------

alter table settings
    add column if not exists country_code_id varchar(10);
alter table settings
    add column if not exists timezone_id varchar(100);

comment on column settings.country_code_id is 'AQR3 CountryCode — the first column of every reporting table. FK to eea_countries.';
comment on column settings.timezone_id is 'AQR3 STA_06 Timezone. FK to eea_timezones; drives the offset on every exported datetime.';

-- ---------------------------------------------------------------------------
-- 2. Release the legacy NOT NULL constraints
--
-- The save endpoint does DELETE FROM settings then
-- INSERT INTO settings (country_code_id, timezone_id) — supplying only two
-- columns. The four v3 columns are NOT NULL with no default, so without this
-- the save swaps one error for another:
--     null value in column "namespace" violates not-null constraint
--
-- The columns themselves are kept rather than dropped: non-destructive, and
-- core/eea/dataflows.py still reads them via `select * from settings` for the
-- XML export on instances where that path currently works.
-- ---------------------------------------------------------------------------

do
$$
    declare
        col text;
    begin
        foreach col in array array['namespace', 'uom_m', 'observation_prefix', 'language_code']
            loop
                if exists (select 1 from information_schema.columns
                           where table_name = 'settings'
                             and column_name = col
                             and is_nullable = 'NO')
                then
                    execute format('alter table settings alter column %I drop not null', col);
                    raise notice 'settings.%: dropped NOT NULL (legacy v3 column)', col;
                end if;
            end loop;
    end
$$;

-- ---------------------------------------------------------------------------
-- 3. Foreign keys, matching schema.sql
--
-- Added unconditionally: an FK against an empty eea_countries is valid, because
-- the only existing values are NULL. Doing it before the backfill keeps the two
-- consistent — the backfill can then only set a value the constraint accepts.
-- ---------------------------------------------------------------------------

do
$$
    begin
        if not exists (select 1 from pg_constraint where conname = 'settings_country_code_id_fkey')
        then
            -- Clear anything that would not satisfy the constraint (e.g. a
            -- 'To-be-defined' placeholder) rather than failing the migration.
            update settings
            set country_code_id = null
            where country_code_id is not null
              and country_code_id not in (select id from eea_countries);

            alter table settings
                add constraint settings_country_code_id_fkey
                    foreign key (country_code_id) references eea_countries on update cascade;
        end if;

        if not exists (select 1 from pg_constraint where conname = 'settings_timezone_id_fkey')
        then
            update settings
            set timezone_id = null
            where timezone_id is not null
              and timezone_id not in (select id from eea_timezones);

            alter table settings
                add constraint settings_timezone_id_fkey
                    foreign key (timezone_id) references eea_timezones on update cascade;
        end if;
    end
$$;

-- ---------------------------------------------------------------------------
-- 4. Backfill the reporting country
--
-- Prefer a real stored value over a guess:
--   a) `country_code` if that column exists and matches an eea_countries id
--   b) otherwise the first dot-segment of `namespace` ('AD.GovernAndorra.AQ' -> 'AD')
--
-- Only a value present in eea_countries is written, because the FK above would
-- reject anything else. If the vocabulary has not been loaded yet nothing is
-- written and section 5 reports the code it *would* have used, so the operator
-- can set it on the Settings page after running populate_vocabularies.py.
-- ---------------------------------------------------------------------------

do
$$
    declare
        n integer;
    begin
        if exists (select 1 from information_schema.columns
                   where table_name = 'settings' and column_name = 'country_code')
        then
            execute $sql$
                update settings s
                set country_code_id = c.id
                from eea_countries c
                where s.country_code_id is null
                  and upper(trim(s.country_code::text)) = upper(c.id)
            $sql$;
            get diagnostics n = row_count;
            if n > 0 then
                raise notice 'settings.country_code_id backfilled from country_code (% row(s))', n;
            end if;
        end if;

        if exists (select 1 from information_schema.columns
                   where table_name = 'settings' and column_name = 'namespace')
        then
            execute $sql$
                update settings s
                set country_code_id = c.id
                from eea_countries c
                where s.country_code_id is null
                  and upper(split_part(s.namespace, '.', 1)) = upper(c.id)
            $sql$;
            get diagnostics n = row_count;
            if n > 0 then
                raise notice 'settings.country_code_id backfilled from namespace (% row(s))', n;
            end if;
        end if;
    end
$$;

-- ---------------------------------------------------------------------------
-- 5. Tell the operator what still has to happen
-- ---------------------------------------------------------------------------

do
$$
    declare
        countries integer;
        timezones integer;
        current_country text;
        detected text;
    begin
        select count(*) into countries from eea_countries;
        select count(*) into timezones from eea_timezones;
        select country_code_id into current_country from settings limit 1;

        -- What the backfill would have used, so the operator has the answer even
        -- when the vocabulary was not loaded in time to apply it.
        if exists (select 1 from information_schema.columns
                   where table_name = 'settings' and column_name = 'namespace')
        then
            execute 'select upper(split_part(namespace, ''.'', 1)) from settings limit 1'
                into detected;
        end if;

        if countries = 0 then
            raise warning
                'eea_countries is empty, so the reporting country could not be set and CountryCode '
                'will be blank in every AQR3 table. Run: python sql/populate_vocabularies.py';
            if detected is not null and detected <> '' then
                raise warning
                    'This database''s namespace suggests the reporting country is %. Set it on the '
                    'Settings page once the vocabularies are loaded.', detected;
            end if;
        end if;
        if timezones = 0 then
            raise warning
                'eea_timezones is empty, so exported datetimes will carry no UTC offset. '
                'Run: python sql/populate_vocabularies.py';
        end if;
        if countries > 0 and current_country is null then
            raise warning
                'settings.country_code_id is not set. CountryCode is the first column of every '
                'AQR3 table and stays blank until it is — set it on the Settings page.';
        end if;
    end
$$;

insert into schema_version (version, description)
values ('4.502.6',
        'Bring settings forward from the v3 shape: add country_code_id/timezone_id, backfill the '
        'reporting country, release the legacy NOT NULL constraints')
on conflict (version) do nothing;

commit;
