from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime


class DataflowModel(BaseModel):
    type: str
    year: int
    timezone: int
    description: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DataflowModelE2a(BaseModel):
    last_request: datetime

    def __getitem__(self, key):
        return super().__getattribute__(key)
