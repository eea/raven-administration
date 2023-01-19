from pydantic import BaseModel
from typing import Optional


class SampleModel(BaseModel):
    id: str
    inlet_height: float
    building_distance: Optional[float] = None
    kerb_distance: Optional[float] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
