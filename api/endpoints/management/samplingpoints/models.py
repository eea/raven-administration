from datetime import datetime
from pydantic import BaseModel


class SamplingPointsModel(BaseModel):
    id: str
    media_monitored: str
    station_id: str
    mobile: bool
    measurement_regime: str
    assessment_type: str
    station_classification: str
    used_aqd: bool
    main_emission_sources: str
    traffic_emissions: str
    heating_emissions: str
    industrial_emissions: str
    distance_source: str
    change_aei_stations: str
    begin_position: str
    end_position: str
    logger_id: str
    pollutant: str
    concentration: str
    timestep: str
    from_time: datetime
    to_time: datetime
    media_monitored_name: str
    station: str
    measurement_regime_name: str
    assessment_type_name: str
    station_classification_name: str
    pollutant_name: str
    concentration_name: str
    timestep_name: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
