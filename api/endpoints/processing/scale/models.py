import string
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScalingpointModel(BaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    sampling_point_id: str
    id: str
    zero_point: float
    span_value: float
    gas_concentration: float
    timestamp: datetime
    current_timestamp: Optional[datetime] = None
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class InsertModel(BaseModel):
    sampling_point_id: str
    zero_point: float
    span_value: float
    gas_concentration: float
    timestamp: datetime
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class PreviewModel(BaseModel):
    sampling_point_id: str
    zero_point: float
    span_value: float
    gas_concentration: float
    timestamp: datetime
    current_timestamp: Optional[datetime] = None
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
