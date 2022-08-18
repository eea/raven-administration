from pydantic import BaseModel
from typing import Optional


class AuthorityModel(BaseModel):
    id: str
    name: str
    organisation: str
    locator: str
    postcode: int
    email: str
    address: str
    phone: str
    website: str
    is_responsible_reporter: Optional[bool] = False

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
