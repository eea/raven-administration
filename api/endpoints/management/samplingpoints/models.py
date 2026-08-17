from core.base_model import RavenBaseModel
from typing import Optional


class SamplingPointsModel(RavenBaseModel):
    id: str
    sampling_point_reference_id: Optional[str] = None
    # The sampling point's active period. from_time is the default AQR3 SPL_03
    # LocationBegin, used whenever sampling_point_locations holds no override for
    # the period — and SPL_03 is part of the AQR3 key, so leaving it unset means
    # SamplingPointLocation.csv reports an empty mandatory column.
    from_time: Optional[str] = None
    to_time: Optional[str] = None
    inlet_height: float
    building_distance: float
    kerb_distance: float
    emission_source_distance: float
    hotspot: bool = False
    logger_id: Optional[str] = None
    private: bool
    use_in_public_api: bool
    daily_check: bool = False
    pollutant_id: int
    time_resolution_id: str
    unit_id: str
    station_id: str
    sampling_point_category_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
