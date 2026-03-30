from pydantic import BaseModel, Field
from typing import Optional, List


class PointModel(BaseModel):
    x: float
    y: float


class SpatialRepresentativenessModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=255)
    sr_application_id: str = Field(..., min_length=1, max_length=255)
    application: str = Field(..., min_length=1, max_length=100)
    points: List[PointModel] = []
    spatial_resolution: Optional[str] = None


class DeleteModel(BaseModel):
    ids: list
