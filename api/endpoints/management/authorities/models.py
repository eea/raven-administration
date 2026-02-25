from pydantic import BaseModel
from core.base_model import RavenBaseModel
from typing import Optional


class AuthorityModel(RavenBaseModel):
    
    id: str
    person_name: Optional[str] = None
    email: str
    organisation_name: str
    organisation_url: Optional[str] = None
    organisation_address: Optional[str] = None
    instance_id: Optional[str] = None
    object_id: Optional[str] = None
    status_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
