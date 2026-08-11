from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class StationModel(RavenBaseModel):
    
    id: str
    station_eoi_code: str
    name: str
    station_national_code: str
    latitude: float
    longitude: float
    altitude: float
    supersite: bool
    station_area_id: str
    network_id: str
    document_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
