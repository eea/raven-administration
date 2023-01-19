from pydantic import BaseModel
from typing import Optional


class NetworkModel(BaseModel):
    id: str
    name: str
    media_id: str
    organisationlevel_id: str
    authority_id: str
    timezone_id: str
    begin_position: str
    end_position: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
