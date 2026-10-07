"""Short codes for the suggested DOC_04 DocumentId prefix.

The v502 reporting guide leaves DocumentId format-free, but "strongly suggests"
starting it with a fixed string for its type, and its examples mostly read
DOC_<document type>_<data table>_<rest>: DOC_DQ_SPP_DU0005_1, DOC_EQ_SPP_...,
DOC_PR_SPP_..., DOC_NET_DU01. The Documents dialog builds that first part from
its two dropdowns, and the user types the rest.

The data table codes are the eea_datatable notations (ARZ, CPL, STA, MOE, ADJ,
SPP, SAP). The aq/documentobject vocabulary was unavailable when this was
written (dd.eionet 404/500), so the document type codes are the guide's own,
with a fallback for terms it does not use.
"""
import re

# The guide's document types -> the codes its examples use.
DOCUMENT_TYPE_CODES = {
    'NetworkDocument': 'NET',
    'DataQualityDocument': 'DQ',
    'EquivalenceDemonstrationDocument': 'EQ',
    'ProcessDocumentation': 'PR',
    'ModelDocument': 'MR',
    'ClassificationDocument': 'CL',
    'SourceAppDocument': 'SAP',
    'PlanDocument': 'PLA',
}

_WORDS = re.compile(r'[A-Z][a-z0-9]*')


def document_type_code(notation):
    """The short code for a document type notation, e.g. DataQualityDocument -> DQ."""
    if not notation:
        return ''
    if notation in DOCUMENT_TYPE_CODES:
        return DOCUMENT_TYPE_CODES[notation]
    words = _WORDS.findall(notation)
    # CamelCase: the initials of the words before "Document"/"Documentation".
    if len(words) > 1 and ''.join(words) == notation:
        kept = [w for w in words if not w.startswith('Document')] or words
        return ''.join(w[0] for w in kept).upper()
    # One word, or an acronym like AQD: its first three letters.
    return re.sub(r'[^A-Za-z0-9]', '', notation)[:3].upper()


def data_table_code(notation):
    """The short code for a data table: its notation as it stands (SPP, ARZ, ...)."""
    return (notation or '').upper()
