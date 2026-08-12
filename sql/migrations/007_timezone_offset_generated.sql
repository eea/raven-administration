-- ===========================================================================
-- 007 — Make eea_timezones.timezone_offset a generated column
--
-- schema.sql declares it as GENERATED ALWAYS ... STORED, derived from `notation`:
--     'UTC'     -> 'Z'
--     'UTC+01'  -> '+01:00'
--     'UTC-03'  -> '-03:00'
--
-- On databases created before that it exists as a plain varchar and was never
-- populated, so every row is NULL. Same class of drift as `settings` in 006:
-- schema.sql was changed in place and nothing carried existing installs forward.
--
-- The effect is easy to miss and wrong in a way Reportnet3 cares about: the AQR3
-- export reads this column for the reporting timezone, so with it NULL **every
-- exported datetime is emitted with no UTC offset** — Start, End, ResultTime,
-- LocationBegin, ProcessActivityBegin, across every table.
--
-- Rebuilding the column rather than back-filling it means new vocabulary rows
-- stay correct without anyone remembering to update them.
--
-- Idempotent, and a no-op where the column is already generated.
-- ===========================================================================

begin;

do
$$
    declare
        is_generated text;
        fixed        integer;
    begin
        select c.is_generated into is_generated
        from information_schema.columns c
        where c.table_name = 'eea_timezones' and c.column_name = 'timezone_offset';

        if is_generated is null then
            raise notice 'eea_timezones.timezone_offset does not exist — adding it as generated';
        elsif is_generated = 'ALWAYS' then
            raise notice 'eea_timezones.timezone_offset is already generated — nothing to do';
            return;
        else
            -- Derived data, so dropping loses nothing. No CASCADE on purpose: if a
            -- view or index depends on it the migration should fail loudly rather
            -- than quietly destroy it.
            alter table eea_timezones drop column timezone_offset;
            raise notice 'eea_timezones.timezone_offset dropped (plain column, was NULL on every row)';
        end if;

        alter table eea_timezones
            add column timezone_offset varchar(10) generated always as (
                CASE
                    WHEN ((notation)::text = 'UTC'::text) THEN 'Z'::text
                    WHEN ((notation)::text ~~ 'UTC+%'::text)
                        THEN (replace((notation)::text, 'UTC'::text, ''::text) || ':00'::text)
                    WHEN ((notation)::text ~~ 'UTC-%'::text)
                        THEN (replace((notation)::text, 'UTC'::text, ''::text) || ':00'::text)
                    ELSE NULL::text
                    END) stored;

        select count(*) into fixed from eea_timezones where timezone_offset is not null;
        raise notice 'eea_timezones.timezone_offset regenerated — % row(s) now resolve an offset', fixed;
    end
$$;

comment on column eea_timezones.timezone_offset is 'ISO 8601 offset (+02:00, Z) derived from notation. Read by the AQR3 export for every datetime, so it must never be NULL for the reporting timezone.';

-- Report any vocabulary row whose notation the expression cannot interpret: those
-- would silently export datetimes without an offset if one were ever selected as
-- the reporting timezone.
do
$$
    declare
        unresolved text;
    begin
        select string_agg(coalesce(notation, '(null)'), ', ' order by notation)
        into unresolved
        from eea_timezones
        where timezone_offset is null;

        if unresolved is not null then
            raise warning
                'eea_timezones rows with no derivable offset: %. Selecting one of these as the '
                'reporting timezone would export every datetime without a UTC offset.', unresolved;
        end if;
    end
$$;

insert into schema_version (version, description)
values ('4.502.7',
        'Make eea_timezones.timezone_offset a generated column so exported datetimes carry the '
        'reporting UTC offset (it was a plain NULL column on pre-v4 databases)')
on conflict (version) do nothing;

commit;
