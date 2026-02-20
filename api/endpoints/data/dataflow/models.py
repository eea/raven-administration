from core.base_model import RavenBaseModel
from typing import List
from datetime import datetime


class DataflowModel(RavenBaseModel):
    type: str
    year: int
    timezone: int
    description: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DataflowModelE2a(RavenBaseModel):
    last_request: datetime

    def __getitem__(self, key):
        return super().__getattribute__(key)
