from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class NetworkModel(RavenBaseModel):
    
    id: str
    name: str
    network_organisational_level_id: str
    timezone_id: Optional[str] = None
    network_document_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
