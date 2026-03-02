from pydantic import BaseModel
from core.base_model import RavenBaseModel


class AuthorityModel(RavenBaseModel):
    
    id: str
    person_name: str
    email: str
    organisation_name: str
    organisation_url: str
    organisation_address: str
    instance_id: str
    object_id: str
    status_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
