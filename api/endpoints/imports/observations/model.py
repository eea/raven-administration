from pydantic import BaseModel
from typing import Optional
from pytz import timezone
from typing import List


class LoggerValue(BaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class LoggerValues(BaseModel):
    values: list[LoggerValue]

    def __getitem__(self, key):
        return super().__getattribute__(key)
