from pydantic import BaseModel
from typing import Optional


class ZoneModel(BaseModel):
    id: str
    name: str
    code: str
    year: int
    area: float
    type_id: str
    population: int
    population_year: int
    authority_id: str
    geojson: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
