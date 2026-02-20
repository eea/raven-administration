from core.base_model import RavenBaseModel
from pydantic import field_validator
from typing import List
from datetime import datetime


class ObservationModel(RavenBaseModel):
    sampling_point_ids: List[str]
    from_dt: datetime
    to_dt: datetime
    meantype: int
    coverage: int

    @field_validator('sampling_point_ids')
    @classmethod
    def validate_sampling_point_ids(cls, v):
        if len(v) < 1:
            raise ValueError('sampling_point_ids must contain at least one item')
        return v

    def __getitem__(self, key):
        return super().__getattribute__(key)
