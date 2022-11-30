from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SamplingPointsModel(BaseModel):
    id: str
    station_id: str
    pollutant_id: str
    timestep_id: str
    concentration_id: str
    station_classification_id: str
    media_id: str
    measurement_regime_id: str
    assessment_type_id: str
    begin_position: str
    mobile: bool
    private: bool

    main_emission_sources: Optional[str] = None
    traffic_emissions: Optional[str] = None
    heating_emissions: Optional[str] = None
    industrial_emissions: Optional[str] = None
    distance_source: Optional[str] = None
    change_aei_stations: Optional[str] = None
    end_position: Optional[str] = None
    logger_id: Optional[str] = None
    used_aqd: Optional[bool] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
