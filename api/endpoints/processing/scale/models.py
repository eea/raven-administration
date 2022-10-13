import string
from pydantic import BaseModel
from typing import Optional


class ScalingpointModel(BaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
