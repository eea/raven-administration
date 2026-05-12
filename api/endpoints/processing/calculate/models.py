from ast import operator
import string
from pydantic import BaseModel
from typing import Optional


class InsertModel(BaseModel):
    primary: str
    secondary: str
    result: str
    operator: str
    create_group: Optional[bool] = False

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    id: int
    primary: str
    secondary: str
    result: str
    operator: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
