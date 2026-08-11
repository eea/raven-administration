from pydantic import BaseModel
from core.base_model import RavenBaseModel


class AuthorityModel(RavenBaseModel):
    
    id: str
    person_name: str
    email: str
    authority_name: str
    authority_url: str
    authority_address: str
    authority_instance_id: str
    authority_role_id: str
    authority_status_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
