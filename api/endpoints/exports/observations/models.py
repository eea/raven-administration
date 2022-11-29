from pydantic import BaseModel, conlist
from typing import List
from datetime import datetime


class ObservationModel(BaseModel):
    sampling_point_ids: conlist(str, min_items=1)
    from_dt: datetime
    to_dt: datetime
    meantype: int
    coverage: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
