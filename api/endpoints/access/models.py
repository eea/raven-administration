from xmlrpc.client import Boolean
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
    network: Optional[Boolean] = False
    observations: Optional[Boolean] = False
    exporting: Optional[Boolean] = False
    processing: Optional[Boolean] = False
    qualitycontrol: Optional[Boolean] = False
    users: Optional[Boolean] = False
    allnetworks: Optional[Boolean] = False
    networks: conlist(str, min_items=0)

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateGroupModel(BaseModel):
    id: int
    name: str
    network: Optional[Boolean] = False
    observations: Optional[Boolean] = False
    exporting: Optional[Boolean] = False
    processing: Optional[Boolean] = False
    qualitycontrol: Optional[Boolean] = False
    users: Optional[Boolean] = False
    allnetworks: Optional[Boolean] = False
    networks: conlist(str, min_items=0)

    def __getitem__(self, key):
        return super().__getattribute__(key)
