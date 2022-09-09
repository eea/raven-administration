from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime


class DataflowModel(BaseModel):
    type: str
    year: int
    timezone: str
    description: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
