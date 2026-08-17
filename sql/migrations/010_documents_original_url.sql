-- ===========================================================================
-- 010 — Add documents.document_original_url (AQR3 DOC_06)
--
-- DOC_06 DocumentOriginalURL is the one AQR3 v5.02 attribute with no column at
-- all: core/reporting/aqr3/spec.py declares Column('DocumentOriginalURL',
-- 'document_original_url') but the DOC SELECT never produces that key, so
-- row.get() returns None and the cell is unconditionally empty. A conformant
-- header over a permanently blank column, which Reportnet3 accepts.
--
-- DOC_05 and DOC_06 are alternatives, not duplicates. A DOC row conveys its
-- document either by naming the PDF the country uploads to Reportnet3 (DOC_05
-- DocumentAttachment) or by pointing at where it is already published (DOC_06),
-- which is the honest answer for a document on a national portal that does not
-- need re-uploading.
--
-- varchar(100) matches the guide. It is tight for a URL and suggests a landing
-- page rather than a deep link; the API refuses longer values with a message
-- rather than truncating, because a silently cut URL is worse than none. The
-- width has been queried with EEA, along with the guide's Content text for
-- DOC_06 which reads "Attached PDF." — copied from DOC_05.
--
-- Note for the CSV round-trip: `documents` has an empty exclusion list in
-- IMPORTABLE/EXPORTABLE, and core/data/management.py requires every column
-- without a default as a CSV header. This column is reportable data rather than
-- an internal, so it deliberately joins the documents CSV contract — existing
-- documents CSVs need the new header added. That break is intended and
-- announced.
--
-- Idempotent, and a no-op once the column exists.
-- ===========================================================================

begin;

do
$$
    declare
        existing text;
    begin
        select data_type into existing
        from information_schema.columns
        where table_name = 'documents' and column_name = 'document_original_url';

        if existing is null then
            alter table documents add column document_original_url varchar(100);
            raise notice 'documents.document_original_url added (AQR3 DOC_06)';
        else
            raise notice 'documents.document_original_url already present — nothing to do';
        end if;
    end
$$;

comment on column documents.document_original_url is 'AQR3 DOC_06 DocumentOriginalURL. Where the document is published, for a document not attached to the Reportnet3 envelope. varchar(100) per the guide; the API refuses longer values rather than truncating.';

insert into schema_version (version, description)
values ('4.502.10',
        'Add documents.document_original_url (AQR3 DOC_06), the only v5.02 attribute with no '
        'column: it was declared in the export spec but never selected, so it exported blank')
on conflict (version) do nothing;

commit;
