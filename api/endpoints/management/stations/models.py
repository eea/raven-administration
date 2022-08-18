from pydantic import BaseModel


class StationModel(BaseModel):
    id: str
    name: str
    eoi_code: str
    network_id: str
    area_classification_id: str
    lat: float
    lng: float
    alt: float
    epsg: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
