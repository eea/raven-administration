from core.base_model import RavenBaseModel
from typing import Optional


class SamplingPointsModel(RavenBaseModel):
    id: str
    inlet_height: float
    building_distance: float
    kerb_distance: float
    emission_source_distance: float
    logger_id: Optional[str] = None
    private: bool
    use_in_public_api: bool
    pollutant_id: int
    time_resolution_id: str
    unit_id: str
    station_id: str
    spo_category_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
