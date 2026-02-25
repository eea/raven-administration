from core.base_model import RavenBaseModel
from typing import Optional


class SamplingPointsModel(RavenBaseModel):
    id: str
    inlet_height: Optional[float] = None
    building_distance: Optional[float] = None
    kerb_distance: Optional[float] = None
    emission_source_distance: Optional[float] = None
    logger_id: Optional[str] = None
    private: bool
    use_in_public_api: bool
    pollutant_id: int
    time_resolution_id: str
    unit_id: str
    station_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
