from typing import Optional
from core.base_model import RavenBaseModel


class ZoneModel(RavenBaseModel):

    id: str
    zone_national_code: str   # AQR3 ARZ_04
    name: str
    zone_area: float          # AQR3 ARZ_05 (km2)
    zone_type_id: Optional[str] = None
    zone_category_id: Optional[str] = None
    geojson: str  # GeoJSON string representation of the geometry
    source_epsg: Optional[int] = 4326  # Source EPSG code, defaults to 4326

    def __getitem__(self, key):
        return super().__getattribute__(key)
