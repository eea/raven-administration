-- ===========================================================================
-- 011 — Migration baseline: the fold-in anchor
--
-- TWO jobs, and both are worth stating.
--
-- 1. It holds the version slot. Migrations 001-010 were folded into
--    sql/schema.sql and moved to sql/migrations/archive/, which
--    apply_migrations.py cannot see — migration_files() (:35) is a
--    NON-recursive glob of *.sql, and that non-recursion is load-bearing.
--    This is the only file left in sql/migrations/, so it must keep a real
--    `insert into schema_version (...) values ('4.502.11'`: VERSION_RE
--    (apply_migrations.py:24-25) requires one in EVERY file, declared_version()
--    (:38-44) raises SystemExit without it, and :147-153 builds the pending list
--    for ALL files before applying any — so one unparseable file aborts the whole
--    run, and docker-entrypoint.sh:15-21 and
--    raven-v4-deploy/docker/Dockerfile.api:48 both exit 1, meaning EVERY API POD
--    REFUSES TO START. Keeping this file also keeps the version scheme showing
--    .11, so the next migration is 012.
--
-- 2. It refuses to record itself against a database that predates the fold-in.
--    apply_migrations.py:150-151 SKIPS this file entirely once 4.502.11 is
--    recorded, so the guard below runs if and only if the database does not
--    record 4.502.11 — which, after the fold-in, means exactly one thing: it is
--    behind. Without the guard such a database would get 4.502.11 recorded and
--    NOTHING run, then report itself fully migrated forever while missing every
--    column 001-010 added; test_all_migrations_are_applied would agree, because
--    it compares recorded versions. `--baseline` bypasses this, as it bypasses
--    every migration body.
--
-- Then, unchanged, its original job:
--
-- Narrow the AQR3 attachment reference columns to varchar(100)
--
-- DOC_05 DocumentAttachment, MRE_11 GeoTiffAttachment and SRE_04
-- GeoTiffAttachment are Reportnet3 `attachment` cells. The cell carries the
-- FILENAME of a file the country uploads to Reportnet3 alongside the CSVs, and
-- the guide declares all three varchar(100). Raven stored them wider —
-- documents.documentattachment varchar(500), the two geotiff_attachment columns
-- varchar(255) — so a reference too long for Reportnet3 could be saved,
-- exported, and only rejected at submission.
--
-- Narrowed rather than left wide and validated only in the API, because the API
-- is not the only write path: the generic CSV import (core/data/management.py)
-- goes straight to SQL and never sees a Pydantic model. A constraint the
-- database enforces covers both.
--
-- Safe now precisely because nothing has ever written these columns — migration
-- 009 established that for documentattachment, and the two external tables are
-- referenced only by the export. The probe below proves it rather than assuming
-- it: if any value is longer than 100 characters the column is left alone and a
-- warning is raised, because silently truncating a filename would point the
-- reference at a file that does not exist.
--
-- Idempotent, and a no-op once each column is varchar(100) or narrower.
-- ===========================================================================

begin;

-- ---------------------------------------------------------------------------
-- Fold-in guard
--
-- One sentinel per folded migration, introspected rather than read from
-- schema_version — so a database restored from a dump that lost its
-- schema_version rows but has all the DDL passes, which a version check would
-- not. Every failure is collected before raising, so the operator gets the whole
-- diagnosis in one run instead of one column per attempt.
--
-- 007 is checked by is_generated, not existence: eea_timezones.timezone_offset
-- existed before as a plain nullable varchar, so only the generated-ness tells a
-- migrated database from an unmigrated one.
-- ---------------------------------------------------------------------------

do
$$
    declare
        missing text[] := '{}';
        generated text;
    begin
        -- 001 sampling point reference / location history
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'sampling_points'
                         and column_name = 'hotspot') then
            missing := missing || '001: sampling_points.hotspot';
        end if;
        if to_regclass('public.sampling_point_locations') is null then
            missing := missing || '001: table sampling_point_locations';
        end if;

        -- 002 AQR3 v5.02 renames and additions
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'stations'
                         and column_name = 'station_eoi_code') then
            missing := missing || '002: stations.station_eoi_code (still eoi_code?)';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'zones'
                         and column_name = 'zone_national_code') then
            missing := missing || '002: zones.zone_national_code (still code?)';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'assessment_regimes'
                         and column_name = 'fixed_measurement_reduction') then
            missing := missing || '002: assessment_regimes.fixed_measurement_reduction';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'observations'
                         and column_name = 'data_capture') then
            missing := missing || '002: observations.data_capture';
        end if;
        if to_regclass('public.spatial_representativeness') is null then
            missing := missing || '002: table spatial_representativeness';
        end if;

        -- 003 the new AQR3 v5.02 tables
        if to_regclass('public.models') is null then
            missing := missing || '003: table models (MOE)';
        end if;
        if to_regclass('public.moe_result_inline') is null then
            missing := missing || '003: table moe_result_inline (MRI)';
        end if;
        if to_regclass('public.moe_result_external') is null then
            missing := missing || '003: table moe_result_external (MRE)';
        end if;
        if to_regclass('public.srs_external') is null then
            missing := missing || '003: table srs_external (SRE)';
        end if;
        if to_regclass('public.pollution_level_adjustment') is null then
            missing := missing || '003: table pollution_level_adjustment (ADJ)';
        end if;
        if to_regclass('public.compliance_assessment_method') is null then
            missing := missing || '003: table compliance_assessment_method (CAM)';
        end if;

        -- 005 daily check / manual log
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'sampling_points'
                         and column_name = 'daily_check') then
            missing := missing || '005: sampling_points.daily_check';
        end if;
        if to_regclass('public.sampling_point_log') is null then
            missing := missing || '005: table sampling_point_log';
        end if;

        -- 006 settings brought forward from the v3 shape
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'settings'
                         and column_name = 'country_code_id') then
            missing := missing || '006: settings.country_code_id';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'settings'
                         and column_name = 'timezone_id') then
            missing := missing || '006: settings.timezone_id';
        end if;

        -- 007 timezone_offset must be GENERATED, not merely present
        select is_generated into generated
        from information_schema.columns
        where table_schema = 'public' and table_name = 'eea_timezones'
          and column_name = 'timezone_offset';
        if generated is null then
            missing := missing || '007: eea_timezones.timezone_offset (absent)';
        elsif generated <> 'ALWAYS' then
            missing := missing || '007: eea_timezones.timezone_offset is not a generated '
                                  'column, so exported datetimes carry no UTC offset';
        end if;

        -- 008 assessment_regime_id rename
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'assessmentdata'
                         and column_name = 'assessment_regime_id') then
            missing := missing || '008: assessmentdata.assessment_regime_id '
                                  '(still assessmentregime_id?)';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'attainments'
                         and column_name = 'assessment_regime_id') then
            missing := missing || '008: attainments.assessment_regime_id '
                                  '(still assessmentregime_id?)';
        end if;

        -- 009 / 010 document attachment and original URL
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'documents'
                         and column_name = 'documentattachment') then
            missing := missing || '009: documents.documentattachment';
        end if;
        if not exists (select 1 from information_schema.columns
                       where table_schema = 'public' and table_name = 'documents'
                         and column_name = 'document_original_url') then
            missing := missing || '010: documents.document_original_url';
        end if;

        if array_length(missing, 1) > 0 then
            raise exception
                'This database predates the migration fold-in: % of the DDL that migrations '
                '001-010 create is absent, so recording 4.502.11 here would mark it fully '
                'migrated while it is not. Missing: %.'
                '%'
                'Bring it forward first — the archived migrations are all idempotent, so '
                'applying them to a database that is only partly behind is safe:'
                '%'
                '  bash:       for f in sql/migrations/archive/0*.sql; do psql "$DB_URI" -f "$f"; done'
                '%'
                '  PowerShell: Get-ChildItem sql/migrations/archive/0*.sql | ForEach-Object '
                '{ psql $env:DB_URI -f $_.FullName }'
                '%'
                'Then re-run sql/apply_migrations.py.',
                array_length(missing, 1), array_to_string(missing, '; '),
                chr(10), chr(10), chr(10), chr(10);
        end if;

        raise notice 'fold-in guard: all DDL from migrations 001-010 is present';
    end
$$;

do
$$
    declare
        target record;
        current_len integer;
        longest integer;
    begin
        for target in
            select * from (values
                ('documents', 'documentattachment', 'AQR3 DOC_05 DocumentAttachment'),
                ('moe_result_external', 'geotiff_attachment', 'AQR3 MRE_11 GeoTiffAttachment'),
                ('srs_external', 'geotiff_attachment', 'AQR3 SRE_04 GeoTiffAttachment')
            ) as t(table_name, column_name, aqr3)
        loop
            select character_maximum_length into current_len
            from information_schema.columns
            where table_name = target.table_name and column_name = target.column_name;

            if current_len is null then
                raise notice '%.% not present — nothing to narrow',
                    target.table_name, target.column_name;
                continue;
            end if;

            if current_len <= 100 then
                raise notice '%.% already varchar(%) — nothing to do',
                    target.table_name, target.column_name, current_len;
                continue;
            end if;

            execute format('select max(length(%I)) from %I', target.column_name,
                           target.table_name) into longest;

            if longest is not null and longest > 100 then
                raise warning
                    '%.% left at varchar(%): a value of % characters exists and would be '
                    'truncated. Shorten the reference(s) to <= 100 characters (the Reportnet3 '
                    'limit for %) and re-run.',
                    target.table_name, target.column_name, current_len, longest, target.aqr3;
                continue;
            end if;

            execute format('alter table %I alter column %I type varchar(100)',
                           target.table_name, target.column_name);
            raise notice '%.% narrowed from varchar(%) to varchar(100) (% row(s) hold a value)',
                target.table_name, target.column_name, current_len,
                coalesce(longest, 0);
        end loop;
    end
$$;

comment on column documents.documentattachment is 'AQR3 DOC_05 DocumentAttachment. The filename of the PDF uploaded to Reportnet3 alongside the CSVs; varchar(100) per the guide. Raven stores the reference, not the file.';
comment on column moe_result_external.geotiff_attachment is 'AQR3 MRE_11 GeoTiffAttachment. The filename of the GeoTIFF uploaded to Reportnet3; varchar(100) per the guide.';
comment on column srs_external.geotiff_attachment is 'AQR3 SRE_04 GeoTiffAttachment. The filename of the GeoTIFF uploaded to Reportnet3; varchar(100) per the guide.';

insert into schema_version (version, description)
values ('4.502.11',
        'Fold-in baseline: migrations 001-010 are in schema.sql. Also narrows the three AQR3 '
        'attachment reference columns to varchar(100) to match the guide, so a reference '
        'Reportnet3 would reject cannot be stored or exported')
on conflict (version) do nothing;

commit;
