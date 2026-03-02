from pydantic import BaseModel
from typing import List


class InsertModel(BaseModel):
    min: float
    max: float
    rep: int
    pollutant_id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    id: int
    min: float
    max: float
    rep: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
