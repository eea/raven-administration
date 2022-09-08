from pydantic import BaseModel


class DatasetModel(BaseModel):
    station_id: str
    year: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class FlagModel(BaseModel):
    sampling_point_id: str
    year: int
    month: int
    level: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
