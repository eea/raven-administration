from core.base_model import RavenBaseModel
from typing import Optional


class SettingsModel(RavenBaseModel):
    id: str
    namespace: str
    uom_m: str
    observation_prefix: str
    language_code: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
