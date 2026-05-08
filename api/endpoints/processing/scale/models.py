import string
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from core.base_model import RavenBaseModel


class ScalingpointModel(BaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(RavenBaseModel):
    sampling_point_id: str
    id: Optional[str] = None
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


class DeleteModel(RavenBaseModel):
    sampling_point_id: str
    timestamp: datetime
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
