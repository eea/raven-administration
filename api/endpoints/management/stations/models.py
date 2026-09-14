from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional
from core.base_model import RavenBaseModel


class StationModel(RavenBaseModel):

    id: str
    # Optional since 4.502.22, which is what migration 013 intended: an EoI code is
    # assigned by EIONET, so a site outside any EEA reporting obligation has none.
    # The column has been nullable since 4.502.13; this model kept demanding a value,
    # so the only way to store an internal site was to invent an identifier -- and 66
    # of 174 stations on the development database are named `NILU-<id>` because of it.
    # Whether the station is reported is report_to_eea below; this is only whether AQR3
    # can name it.
    station_eoi_code: Optional[str] = None
    name: str
    station_national_code: str
    latitude: float
    longitude: float
    altitude: float
    supersite: bool
    station_area_id: str
    network_id: str
    document_id: str
    # Intent. Defaults true so an existing client that does not send the field keeps
    # the behaviour it had before the flag existed.
    report_to_eea: bool = True

    @field_validator('station_eoi_code', mode='after')
    @classmethod
    def _blank_is_no_code(cls, value):
        """'' means "no EoI code", and must reach the database as NULL.

        RavenBaseModel strips whitespace, so a form field the user cleared arrives as
        ''. An empty string satisfies `station_eoi_code IS NOT NULL`, so without this
        the station would be exported to Reportnet 3 with an empty StationEoICode --
        a mandatory, primary-key column.
        """
        return value or None

    def __getitem__(self, key):
        return super().__getattribute__(key)
