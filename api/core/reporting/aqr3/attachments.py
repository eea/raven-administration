"""Validation for the AQR3 `attachment` reference columns.

DOC_05 DocumentAttachment, MRE_11 GeoTiffAttachment and SRE_04 GeoTiffAttachment
are Reportnet3 `attachment` cells. The cell carries the *filename* of a file the
reporting country uploads to Reportnet3 alongside the CSVs — raven records the
reference and does not store the file, so what is validated here is the name, not
its contents.

Kept in one module because the same two rules apply to all three, and a rule
enforced in one route and forgotten in another is how a reference Reportnet3
rejects reaches a submission:

  * at most 100 characters, the width the guide declares (and, since migration
    011, the width of the column);
  * an extension appropriate to the attribute — the guide says "Attached PDF."
    for DOC_05 and "Attached GEOTIFF." for the other two.

A bare filename is expected rather than a path: it has to match what was uploaded
to Reportnet3, and a directory component would not.

DOC_05 may also be an http(s) URL. Reportnet 3.0 will take a document attachment
by URL (4sFera, 2026-10-07): either one the document already has, or the one Raven
gives a PDF uploaded to it (document_files, /api/public/documents/<token>.pdf).
The GeoTIFF attachments stay filenames.
"""
import re

MAX_LENGTH = 100

# attribute code -> (permitted extensions, what the guide calls it)
KINDS = {
    'DOC_05': (('.pdf',), 'PDF'),
    'MRE_11': (('.tif', '.tiff'), 'GeoTIFF'),
    'SRE_04': (('.tif', '.tiff'), 'GeoTIFF'),
}

_PATH_SEPARATOR = re.compile(r'[\\/]')
_URL = re.compile(r'https?://[^\s/]+/\S*', re.IGNORECASE)

# attribute codes whose reference may be a URL instead of a filename
URL_KINDS = {'DOC_05'}


class AttachmentReferenceError(ValueError):
    """A filename Reportnet3 would not accept for this attribute."""


def validate_reference(kind, value):
    """Check an attachment filename (or, for DOC_05, URL), returning it unchanged so it can be used inline.

    None and '' pass: an attachment is optional for every one of the three
    attributes, and a document may instead be referenced by DOC_06
    DocumentOriginalURL.
    """
    if value in (None, ''):
        return value

    extensions, label = KINDS[kind]

    if len(value) > MAX_LENGTH:
        raise AttachmentReferenceError(
            f'{kind}: the attachment reference is {len(value)} characters; Reportnet3 allows '
            f'at most {MAX_LENGTH}. Rename the file before uploading it.')

    if kind in URL_KINDS and _URL.fullmatch(value):
        return value

    if _PATH_SEPARATOR.search(value):
        raise AttachmentReferenceError(
            f'{kind}: give the file name only ({value.split("/")[-1].split(chr(92))[-1]}), not a '
            f'path — it has to match the name of the file uploaded to Reportnet3.'
            + (' A URL must start with http:// or https://.' if kind in URL_KINDS else ''))

    if not value.lower().endswith(extensions):
        raise AttachmentReferenceError(
            f'{kind}: expected {label} ({", ".join(extensions)}), got {value!r}.')

    return value
