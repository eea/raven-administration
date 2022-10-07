from datetime import datetime
from pydantic import BaseModel


class ObservingCapabilityModel(BaseModel):
    id: str
    begin_position: datetime
    end_position: datetime
    process_type: str
    result_nature: str
    sampling_point_id: str
    process_id: str
    sample_id: str
    process_type_name: str
    result_nature_name: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
