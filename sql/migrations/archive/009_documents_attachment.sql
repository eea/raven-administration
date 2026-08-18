-- ===========================================================================
-- 009 — Reconcile documents.documentattachment
--
-- Two failures with one cause: the column is declared in schema.sql but no
-- application code ever writes it. Repo-wide it appears exactly twice — the
-- declaration at schema.sql, and `d.documentattachment` in the AQR3 DOC export.
--
--   * Databases created before it (dev-raven4) do not have the column at all,
--     because `create table if not exists documents` is a no-op on an existing
--     table and no migration ever added it. Exporting Documentation.csv fails
--     with `column d.documentattachment does not exist` — a 500 on the Dataflow
--     Export page. Same drift class as 006 (settings), 007 (timezone_offset)
--     and 008 (assessment_regime_id).
--
--   * Databases that do have it (raven-airquis, every fresh install) declare it
--     NOT NULL with no default, while the documents CRUD inserts only
--     (id, datatable_id, documentobject_id) — see
--     api/endpoints/management/documents/routes.py. So creating a document
--     fails with a not-null violation. That has stayed hidden only because
--     those databases have no documents yet.
--
-- Making the column nullable fixes both and is the truthful modelling: raven
-- does not capture document attachments today. AQR3 DOC_05 DocumentAttachment
-- then exports blank, which is accurate — the same position DOC_06
-- DocumentOriginalURL is already in. Wiring up an actual attachment is a
-- feature, not part of unbreaking the export.
--
-- Idempotent, and a no-op once the column exists and is nullable.
-- ===========================================================================

begin;

do
$$
    declare
        nullable text;
        n        bigint;
    begin
        select is_nullable into nullable
        from information_schema.columns
        where table_name = 'documents' and column_name = 'documentattachment';

        if nullable is null then
            alter table documents add column documentattachment varchar(500);
            select count(*) into n from documents;
            raise notice
                'documents.documentattachment added as nullable (% existing row(s) left NULL — '
                'raven has never recorded attachments, so there is no value to backfill)', n;

        elsif nullable = 'NO' then
            alter table documents alter column documentattachment drop not null;
            raise notice
                'documents.documentattachment: dropped NOT NULL (nothing writes it, so the '
                'constraint made the documents CRUD unable to insert)';

        else
            raise notice 'documents.documentattachment already nullable — nothing to do';
        end if;
    end
$$;

comment on column documents.documentattachment is 'AQR3 DOC_05 DocumentAttachment. Nullable: no part of raven writes this yet, so it exports blank until an attachment path is added.';

insert into schema_version (version, description)
values ('4.502.9',
        'Add documents.documentattachment where missing and make it nullable: fixes the 500 on the '
        'Documentation CSV export and the not-null violation when creating a document')
on conflict (version) do nothing;

commit;
