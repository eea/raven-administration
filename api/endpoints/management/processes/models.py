from core.base_model import RavenBaseModel
from typing import Optional
from pydantic import field_validator
from datetime import datetime


class ProcessModel(RavenBaseModel):
    id: str
    activity_begin: str
    activity_end: Optional[str] = None
    data_quality_document_id: str
    equivalence_demonstration_document_id: str
    process_document_id: str
    measurement_type_id: str
    method_id: str
    equipment_id: str
    analytical_technique_id: str
    equivalence_demonstrated_id: str
    sampling_point_id: str
    equipment_identifier: Optional[str] = None

    @field_validator('activity_begin', 'activity_end')
    @classmethod
    def validate_datetime_format(cls, v):
        if v is None or v == '':
            return None
        
        # Strip timezone offset if present (e.g., +01:00, -05:00, Z)
        import re
        v_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', v)
        v_clean = v_clean.rstrip('Z')
        
        # Try to parse various datetime formats and normalize to YYYY-MM-DD HH:MM:SS
        formats_to_try = [
            '%Y-%m-%d %H:%M:%S',      # Already correct format
            '%Y-%m-%d',                # Date only, add time
            '%Y-%m-%dT%H:%M:%S',       # ISO format with T
            '%Y-%m-%d %H:%M',          # Without seconds
            '%d/%m/%Y %H:%M:%S',       # European format
            '%d/%m/%Y',                # European date only
            '%Y/%m/%d %H:%M:%S',       # Alternative separator
            '%Y/%m/%d',                # Alternative separator, date only
        ]
        
        for fmt in formats_to_try:
            try:
                dt = datetime.strptime(v_clean, fmt)
                # Always return in the required format: YYYY-MM-DD HH:MM:SS
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        
        # If none of the formats match, raise validation error
        raise ValueError(
            f'Invalid datetime format: "{v}". Expected format: YYYY-MM-DD HH:MM:SS '
            f'or YYYY-MM-DD (time will default to 00:00:00)'
        )

    def __getitem__(self, key):
        return super().__getattribute__(key)
