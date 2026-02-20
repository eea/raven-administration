from pydantic import BaseModel
from core.base_model import RavenBaseModel


class ZoneModel(RavenBaseModel):
    
    id: str
    name: str
    code: str
    year: int
    area: float
    zone_type_id: str
    population: int
    population_year: int
    authority_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
