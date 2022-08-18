import string
from pydantic import BaseModel
from typing import Optional


class InsertModel(BaseModel):
    oc_id: str
    source_id: str
    target_id: str
    factor: float
    createdby: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    id: int
    source_id: str
    target_id: str
    factor: float

    def __getitem__(self, key):
        return super().__getattribute__(key)
