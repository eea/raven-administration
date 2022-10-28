from pydantic import BaseModel, conlist
from typing import Optional
from pytz import timezone


class InsertModel(BaseModel):
    name: str
    username: str
    password: str
    groups: conlist(str, min_items=1)
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    id: int
    name: str
    username: str
    password: Optional[str] = None
    groups: conlist(str, min_items=1)
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class InsertGroupModel(BaseModel):
    name: str
    network: Optional[bool] = False
    observations: Optional[bool] = False
    exporting: Optional[bool] = False
    processing: Optional[bool] = False
    qualitycontrol: Optional[bool] = False
    users: Optional[bool] = False
    allnetworks: Optional[bool] = False
    networks: conlist(str, min_items=0)

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateGroupModel(BaseModel):
    id: int
    name: str
    network: Optional[bool] = False
    observations: Optional[bool] = False
    exporting: Optional[bool] = False
    processing: Optional[bool] = False
    qualitycontrol: Optional[bool] = False
    users: Optional[bool] = False
    allnetworks: Optional[bool] = False
    networks: conlist(str, min_items=0)

    def __getitem__(self, key):
        return super().__getattribute__(key)
