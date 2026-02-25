from pydantic import BaseModel
from typing import Optional

# accept an array of model object


class AqiModel(BaseModel):
    level: int
    description: str
    color: str
    pollutant_id: int
    timestep_id: str
    range_from: float
    range_to: float

    def __getitem__(self, key):
        return super().__getattribute__(key)


class AqiListModel(BaseModel):
    __root__: list[AqiModel]
