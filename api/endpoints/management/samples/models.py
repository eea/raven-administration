from datetime import datetime
from pydantic import BaseModel


class SampleModel(BaseModel):
    id: str
    inlet_height: float
    building_distance: float
    kerb_distance: float

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
