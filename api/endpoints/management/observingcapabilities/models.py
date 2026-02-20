from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class ObservingCapabilityModel(RavenBaseModel):
    id: str
    begin_position: str
    process_type_id: str
    result_nature_id: str
    sampling_point_id: str
    process_id: str
    sample_id: str

    end_position: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
