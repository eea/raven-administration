from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class Processvalue(BaseModel):
    sampling_point_id: str
    begin_position: datetime
    end_position: datetime
    value: float
    verification_flag: int
    validation_flag: int
    import_value: Optional[float]

    ts_from_epoch: Optional[float]
    ts_to_epoch: Optional[float]
    ts_timestep: Optional[int]
    ts_is_calculated: Optional[bool]
    has_timeserie_info: bool = False

    def __getitem__(self, key):
        return super().__getattribute__(key)
