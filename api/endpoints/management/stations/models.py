from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class StationModel(RavenBaseModel):
    
    id: str
    eoi_code: str
    name: str
    national_code: str
    latitude: float
    longitude: float
    altitude: float
    supersite: bool
    area_classification_id: str
    network_id: str
    document_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
