from datetime import datetime
from pydantic import BaseModel


class StationModel(BaseModel):
    id: str
    name: str
    begin_position: datetime
    end_position: datetime
    network_id: str
    city: str
    national_station_code: str
    media_monitored: str
    mobile: bool
    measurement_regime: str
    area_classification: str
    distance_junction: int
    traffic_volume: int
    heavy_duty_fraction: float
    height_facades: int
    municipality: str
    street_width: int
    eoi_code: str
    longitude: float
    latitude: float
    altitude: float
    epsg: int
    network: str
    media_monitored_name: str
    measurement_regime_name: str
    area_classification_name: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
