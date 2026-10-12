"""AQR3 SRS SpatialRepresentativeness, one row per SRS application.

The guide keys SRS on (CountryCode, SRSId, SRSApplicationId): SRS_02 SRSId names an
area, and SRS_03 SRSApplicationId one use of it -- SPO representativeness or
exceedance extent (SRS_04). The grid cells (SRI) and the GeoTIFF (SRE) belong to the
application, so srs_application_id is the key here; srs_id is shared by an area's
applications and is what CAM_16 links to.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class PointModel(BaseModel):
    x: float
    y: float


class SpatialRepresentativenessModel(BaseModel):
    # SRS_02 and SRS_03, varchar(50) in the guide.
    srs_id: str = Field(..., min_length=1, max_length=50)
    # Derived by the API from srs_id and the application when left empty.
    srs_application_id: Optional[str] = Field(None, max_length=50)
    # SRS_04: spo_sr | exc_sr (eea_srapplication).
    srs_application: str = Field(..., min_length=1, max_length=100)
    # SRS_05: inline (SRI grid cells) | external (an SRE GeoTIFF).
    result_encoding_id: str = Field('inline', min_length=1, max_length=100)
    # SRS_06: the model/OBE that defined the area. Checked against models.
    representativeness_assessment_method_id: Optional[str] = Field(None, max_length=255)
    # SRI_05 / SRE_03, an integer number of metres (10 | 100 | 1000 | 10000).
    spatial_resolution: Optional[int] = None
    # SRE_04: the filename of the GeoTIFF uploaded to Reportnet3. External only.
    geotiff_attachment: Optional[str] = Field(None, max_length=100)
    # Where an inline area comes from: points as JSON (the API's original shape), a
    # file staged by /parse (what the form sends), or another application's cells
    # (Duplicate). See routes._store_area.
    points: List[PointModel] = []
    upload_token: Optional[str] = Field(None, max_length=32)
    copy_cells_from: Optional[str] = Field(None, max_length=50)


class SrImportModel(SpatialRepresentativenessModel):
    """A CSV row: an SR application without its area. The area fields are excluded
    rather than left at their defaults, so a file cannot name them and the template
    does not show them."""
    points: List[PointModel] = Field(default=[], exclude=True)
    upload_token: Optional[str] = Field(None, exclude=True)
    copy_cells_from: Optional[str] = Field(None, exclude=True)


class DeleteModel(BaseModel):
    ids: list
