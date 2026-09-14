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
    # Optional since 4.502.22, which is what migration 012 intended: NULL means the
    # component has no EEA pollutant code, and the local component is identified by
    # plugin_sp_extended.plugin_pollutant_id instead. The column has been nullable
    # since 4.502.12; this model kept demanding a value, so a local component could
    # not be stored without borrowing someone else's code.
    pollutant_id: Optional[int] = None
    time_resolution_id: str
    unit_id: str
    station_id: str
    sampling_point_category_id: str
    # Intent, ANDed with the station's own flag. Defaults true so an existing client
    # that does not send the field keeps the behaviour it had before the flag existed.
    report_to_eea: bool = True

    def __getitem__(self, key):
        return super().__getattribute__(key)
