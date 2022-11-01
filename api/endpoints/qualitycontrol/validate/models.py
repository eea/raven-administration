from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime


class TimevalueModel(BaseModel):
    sampling_point_id: str
    from_dt: datetime
    to_dt: datetime

    def __getitem__(self, key):
        return super().__getattribute__(key)


class FlagModel(BaseModel):
    ids: conlist(str, min_items=1)
    flag: int
    sampling_point_id: str

    @property
    def ids_tuple(self) -> tuple:
        return tuple(self.ids)

    def __getitem__(self, key):
        return super().__getattribute__(key)
