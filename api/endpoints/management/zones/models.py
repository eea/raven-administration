from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class ZoneModel(RavenBaseModel):
    
    id: str
    code: str
    name: str
    area: float
    zone_type_id: Optional[str] = None
    zone_category_id: Optional[str] = None
    geojson: str  # GeoJSON string representation of the geometry
    source_epsg: Optional[int] = 4326  # Source EPSG code, defaults to 4326

    def __getitem__(self, key):
        return super().__getattribute__(key)
