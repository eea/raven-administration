-- ===========================================================================
-- 026 — Raven stores documents, and DOC_05 may be a URL
--
-- AQR3 DOC_05 DocumentAttachment was the filename of a PDF the country uploads
-- to Reportnet3 next to the CSVs; Raven kept the name and never the file.
-- Reportnet 3.0 will instead take the attachment by URL (4sFera, 2026-10-07),
-- and Raven offers two ways to give one:
--
--   * paste a permanent URL the document already has, or
--   * upload the PDF to Raven, which keeps it here and serves it without login
--     at /api/public/documents/<token>.pdf -- that URL goes into DOC_05.
--
-- The file is kept in the database rather than on a volume: dev-raven4 runs two
-- API replicas, which a ReadWriteOnce volume cannot serve, and a database backup
-- or swap then carries the documents with it.
--
-- Every upload is a new row under a new random token, so a URL already
-- submitted keeps returning the bytes it returned then. Deleting the document
-- deletes its files, and with them its URLs.
--
-- Idempotent. schema.sql carries the same DDL and seeds this version.
-- ===========================================================================

begin;

create table if not exists document_files
(
    token       varchar(32)  not null primary key,
    document_id varchar(255) not null
        references documents (id) on update cascade on delete cascade,
    filename    varchar(255) not null,
    mime_type   varchar(100) not null default 'application/pdf',
    file_size   integer      not null,
    sha256      char(64)     not null,
    content     bytea        not null,
    uploaded_by varchar(255),
    uploaded_at timestamp    not null default current_timestamp
);

comment on table document_files is 'PDFs uploaded for documents. Served without login at /api/public/documents/<token>.pdf, the URL Raven writes to documents.documentattachment (DOC_05). One row per upload; a token is never reused.';
comment on column document_files.token is 'Random hex; the key of the public URL. Unguessable, so the URL is the only way to the file.';
comment on column document_files.filename is 'The name the file was uploaded with, used as the download name.';

create index if not exists idx_document_files_document
    on document_files (document_id);

comment on column documents.documentattachment is 'AQR3 DOC_05 DocumentAttachment. Either the filename of a PDF uploaded to Reportnet3 alongside the CSVs, or a URL to the PDF -- one the user pasted, or Raven''s own for a file in document_files. varchar(100) per the guide.';

insert into schema_version (version, description)
values ('4.502.26', 'document_files: PDFs uploaded for documents, served by public URL; '
                    'DOC_05 DocumentAttachment may be a URL')
on conflict (version) do nothing;

commit;
