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
    # AQR3 SRS_05 — whether the area is given inline as grid cells or as an
    # external GeoTIFF. FK to eea_resultencoding.
    result_encoding_id: Optional[str] = Field(None, max_length=100)
    # AQR3 SRS_06 — the assessment method this area is representative of: a
    # sampling point for spo_sr, a model for exc_sr. No vocabulary; the guide
    # cross-checks it against the SamplingPoint and Model tables.
    representativeness_assessment_method_id: Optional[str] = Field(None, max_length=255)


class DeleteModel(BaseModel):
    ids: list
