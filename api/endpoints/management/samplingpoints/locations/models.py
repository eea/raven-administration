"""AQR3 SPL SamplingPointLocation — per-period location overrides.

The AQR3 key is (CountryCode, AssessmentMethodId, LocationBegin), so
`location_begin` is both part of the key and an editable value. The request
therefore carries the key separately from the values: moving a period's start is
then an explicit key change rather than an insert that silently leaves the
original row behind.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class LocationKey(RavenBaseModel):
    """Identifies an existing period."""
    sampling_point_id: str
    location_begin: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class LocationModel(RavenBaseModel):
    """One location period. Every attribute is optional and falls back to the
    values on sampling_points/stations, which is what the SPL export COALESCEs
    down to — so an override row need only carry what actually changed."""
    sampling_point_id: str
    location_begin: str                       # AQR3 SPL_03, required
    location_end: Optional[str] = None        # AQR3 SPL_04, NULL means current
    station_area_id: Optional[str] = None     # SPL_05
    sampling_point_category_id: Optional[str] = None   # SPL_06
    hotspot: Optional[bool] = None            # SPL_07
    supersite: Optional[bool] = None          # SPL_08
    latitude: Optional[float] = None          # SPL_09
    longitude: Optional[float] = None         # SPL_10
    altitude: Optional[float] = None          # SPL_11
    inlet_height: Optional[float] = None      # SPL_12
    building_distance: Optional[float] = None  # SPL_13
    kerb_distance: Optional[float] = None     # SPL_14
    emission_source_distance: Optional[float] = None   # SPL_15

    def __getitem__(self, key):
        return super().__getattribute__(key)
