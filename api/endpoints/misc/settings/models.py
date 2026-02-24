from core.base_model import RavenBaseModel


class SettingsModel(RavenBaseModel):
    country_code_id: str
    timezone_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
