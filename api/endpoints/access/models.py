from core.base_model import RavenBaseModel
from pydantic import field_validator
from typing import Optional, List
from pytz import timezone


class InsertModel(RavenBaseModel):
    name: str
    username: str
    password: str
    groups: List[str]
    createdby: Optional[str] = None

    @field_validator('groups')
    @classmethod
    def validate_groups(cls, v):
        if len(v) < 1:
            raise ValueError('groups must contain at least one item')
        return v

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(RavenBaseModel):
    id: int
    name: str
    username: str
    password: Optional[str] = None
    groups: List[str]
    createdby: Optional[str] = None

    @field_validator('groups')
    @classmethod
    def validate_groups(cls, v):
        if len(v) < 1:
            raise ValueError('groups must contain at least one item')
        return v

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(RavenBaseModel):
    id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class InsertGroupModel(RavenBaseModel):
    name: str
    management: Optional[bool] = False
    data: Optional[bool] = False
    exporting: Optional[bool] = False
    processing: Optional[bool] = False
    qualitycontrol: Optional[bool] = False
    users: Optional[bool] = False
    allnetworks: Optional[bool] = False
    networks: List[str] = []

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateGroupModel(RavenBaseModel):
    id: int
    name: str
    management: Optional[bool] = False
    data: Optional[bool] = False
    exporting: Optional[bool] = False
    processing: Optional[bool] = False
    qualitycontrol: Optional[bool] = False
    users: Optional[bool] = False
    allnetworks: Optional[bool] = False
    networks: List[str] = []

    def __getitem__(self, key):
        return super().__getattribute__(key)
