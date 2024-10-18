from pydantic import BaseModel
from typing import Optional


class SettingsModel(BaseModel):
    id: str
    namespace: str
    uom_m: str
    observation_prefix: str
    language_code: str
    country: str
    country_code: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
