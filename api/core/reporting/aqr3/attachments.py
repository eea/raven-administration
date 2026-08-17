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


class AttachmentReferenceError(ValueError):
    """A filename Reportnet3 would not accept for this attribute."""


def validate_reference(kind, value):
    """Check an attachment filename, returning it unchanged so it can be used inline.

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

    if _PATH_SEPARATOR.search(value):
        raise AttachmentReferenceError(
            f'{kind}: give the file name only ({value.split("/")[-1].split(chr(92))[-1]}), not a '
            f'path — it has to match the name of the file uploaded to Reportnet3.')

    if not value.lower().endswith(extensions):
        raise AttachmentReferenceError(
            f'{kind}: expected {label} ({", ".join(extensions)}), got {value!r}.')

    return value
