-- ===========================================================================
-- 027 — an uploaded PDF's URL goes in DOC_06, its filename in DOC_05
--
-- 026 wrote the public URL Raven gives an uploaded PDF
-- (/api/public/documents/<token>.pdf) to documents.documentattachment, AQR3
-- DOC_05. The guide types DOC_05 as a Reportnet3 `attachment` -- the attached
-- file, named by its filename -- and DOC_06 DocumentOriginalURL as a string:
-- where the document is published. A URL is the second, so an upload now sets
-- document_original_url to the URL and documentattachment to the file's name.
--
-- Documents uploaded under 026 are moved the same way: when documentattachment
-- is one of Raven's own document URLs, that URL moves to document_original_url
-- (unless the user has set one) and the attachment becomes the uploaded file's
-- name, cut to the 100 characters DOC_05 allows and still ending in .pdf.
--
-- Idempotent: a moved row no longer matches.
-- ===========================================================================

begin;

update documents d
set document_original_url = coalesce(nullif(d.document_original_url, ''), d.documentattachment),
    documentattachment    = case
        when length(f.filename) <= 100 then f.filename
        else left(regexp_replace(f.filename, '\.[^.]*$', ''), 96) || '.pdf'
    end
from document_files f
where d.documentattachment like '%/api/public/documents/' || f.token || '.pdf'
  and f.document_id = d.id;

comment on column documents.documentattachment is 'AQR3 DOC_05 DocumentAttachment. The filename of the PDF; for a file uploaded to Raven (document_files), the name it was uploaded with. varchar(100) per the guide.';
comment on column documents.document_original_url is 'AQR3 DOC_06 DocumentOriginalURL. Where the document is published: a URL the user gives, or the permanent public URL Raven serves an uploaded PDF at (/api/public/documents/<token>.pdf). varchar(100) per the guide; the API refuses longer values rather than truncating.';
comment on table document_files is 'PDFs uploaded for documents. Served without login at /api/public/documents/<token>.pdf, the URL Raven writes to documents.document_original_url (DOC_06). One row per upload; a token is never reused.';

insert into schema_version (version, description)
values ('4.502.27', 'an uploaded document''s URL goes in document_original_url (DOC_06), '
                    'its filename in documentattachment (DOC_05)')
on conflict (version) do nothing;

commit;
