from core.base_model import RavenBaseModel
from pydantic import field_validator
from typing import List
from datetime import datetime


class TimevalueModel(RavenBaseModel):
    sampling_point_id: str
    from_dt: datetime
    to_dt: datetime

    def __getitem__(self, key):
        return super().__getattribute__(key)


class FlagModel(RavenBaseModel):
    ids: List[str]
    flag: int
    sampling_point_id: str

    @field_validator('ids')
    @classmethod
    def validate_ids(cls, v):
        if len(v) < 1:
            raise ValueError('ids must contain at least one item')
        return v

    @property
    def ids_tuple(self) -> tuple:
        return tuple(self.ids)

    def __getitem__(self, key):
        return super().__getattribute__(key)
