from pydantic import BaseModel


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
    is_responsible_reporter: bool

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
