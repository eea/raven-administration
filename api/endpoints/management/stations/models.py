from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class StationModel(RavenBaseModel):
    
    id: str
    name: str
    network_id: str
    area_classification_id: str
    media_id: str
    measurement_regime_id: str
    eoi_code: str
    longitude: float
    latitude: float
    altitude: Optional[float] = None
    epsg: int
    begin_position: str
    mobile: bool

    national_station_code: Optional[str] = None
    municipality: Optional[str] = None
    city: Optional[str] = None
    street_width: Optional[int] = None
    distance_junction: Optional[int] = None
    traffic_volume: Optional[int] = None
    heavy_duty_fraction: Optional[float] = None
    height_facades: Optional[float] = None
    end_position: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
