"""AQR3 SPP SamplingProcess models.

The AQR3 key is (CountryCode, ProcessId, AssessmentMethodId, ProcessActivityBegin).
CountryCode is instance-wide (settings.country_code_id), so `id`, `sampling_point_id`
and `process_activity_begin` together identify a row. All three are editable, hence the
separate key/values shape on update -- an UPDATE keyed on the new values would match
nothing and leave the original row in place.
"""
import re
from datetime import datetime
from typing import Optional

from pydantic import field_validator

from core.base_model import RavenBaseModel

# The list endpoint renders both timestamps with
# to_char(..., 'YYYY-MM-DD HH24:MI') and Crud.vue's date picker posts back
# 'yyyy-MM-dd HH:00', so the second entry is the round-trip that matters. The rest are
# kept because the CSV round-trip and external callers predate the picker.
_DATETIME_FORMATS = (
    '%Y-%m-%d %H:%M:%S',    # already the storage format
    '%Y-%m-%d %H:%M',       # what the date picker and the list endpoint use
    '%Y-%m-%d',             # date only, midnight
    '%Y-%m-%dT%H:%M:%S',    # ISO with T
    '%d/%m/%Y %H:%M:%S',    # European
    '%d/%m/%Y',
    '%Y/%m/%d %H:%M:%S',
    '%Y/%m/%d',
)


def _normalise_datetime(v):
    """Accept the formats above and normalise to 'YYYY-MM-DD HH:MM:SS'.

    Shared by the key and the values so a timestamp cannot normalise one way when it
    identifies a row and another way when it is written to one -- that would make an
    edit silently miss.
    """
    if v is None or v == '':
        return None

    # Strip a timezone offset if present (e.g. +01:00, -05:00, Z). The column is a
    # naive `timestamp`, so an offset here is noise from whatever produced the string.
    v_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', v).rstrip('Z')

    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(v_clean, fmt).strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    raise ValueError(
        f'Invalid datetime format: "{v}". Expected format: YYYY-MM-DD HH:MM:SS '
        f'or YYYY-MM-DD (time will default to 00:00:00)')


class ProcessKey(RavenBaseModel):
    """Identifies an existing process — the AQR3 SPP primary key."""

    id: str
    sampling_point_id: str
    process_activity_begin: str

    _normalise_begin = field_validator('process_activity_begin')(_normalise_datetime)

    def __getitem__(self, key):
        return super().__getattribute__(key)


class ProcessModel(RavenBaseModel):
    """One sampling process.

    Optional here means nullable in schema.sql, not unimportant: Manager turns a blank
    field into null before posting, so a bare `str` on a nullable column rejects a row
    the database would take. Only the three not-null columns are required, and those
    are exactly the three the AQR3 key is built from.
    """

    id: str                                   # SPP_02, key
    sampling_point_id: str                    # SPP_03, key
    process_activity_begin: str               # SPP_04, key

    process_activity_end: Optional[str] = None                    # SPP_05
    measurement_type_id: Optional[str] = None                     # SPP_07
    method_id: Optional[str] = None                               # SPP_08
    equipment_id: Optional[str] = None                            # SPP_09
    analytical_technique_id: Optional[str] = None                 # SPP_10
    equivalence_demonstrated_id: Optional[str] = None             # SPP_11
    data_quality_document_id: Optional[str] = None                # SPP_12
    equivalence_demonstration_document_id: Optional[str] = None   # SPP_13
    process_document_id: Optional[str] = None                     # SPP_14
    # Raven-internal: the serial or asset tag of the physical analyser. No AQR3
    # equivalent, so it is not exported.
    equipment_identifier: Optional[str] = None

    _normalise_dates = field_validator(
        'process_activity_begin', 'process_activity_end')(_normalise_datetime)

    def __getitem__(self, key):
        return super().__getattribute__(key)
