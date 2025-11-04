from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime


class StatisticsModel(BaseModel):
    year: int
    pollutant: str
    aggregation_process: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
