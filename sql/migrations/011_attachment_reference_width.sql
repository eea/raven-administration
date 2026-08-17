-- ===========================================================================
-- 011 — Narrow the AQR3 attachment reference columns to varchar(100)
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
        'Narrow the three AQR3 attachment reference columns to varchar(100) to match the guide, '
        'so a reference Reportnet3 would reject cannot be stored or exported')
on conflict (version) do nothing;

commit;
