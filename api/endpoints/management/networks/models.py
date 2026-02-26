from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class NetworkModel(RavenBaseModel):
    
    id: str
    name: str
    report_id: str
    administration_level_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
