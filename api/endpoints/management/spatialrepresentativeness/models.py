from pydantic import BaseModel, Field
from typing import Optional, List


class PointModel(BaseModel):
    x: float
    y: float


class SpatialRepresentativenessModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=255)
    srs_application_id: str = Field(..., min_length=1, max_length=255)
    srs_application: str = Field(..., min_length=1, max_length=100)
    points: List[PointModel] = []
    # AQR3 SRI_05 is an integer number of metres (10 | 100 | 1000 | 10000).
    spatial_resolution: Optional[int] = None


class DeleteModel(BaseModel):
    ids: list
