from typing import Optional

from core.base_model import RavenBaseModel


class SettingsModel(RavenBaseModel):
    country_code_id: str
    timezone_id: str

    # Observation Change History defaults: { hidden_columns: [...], rules: [...] }.
    # Optional and defaulting to None so that a client which does not know about the
    # field (an older bundle, or any caller that only wants to change the country)
    # leaves the stored value alone rather than clearing it. settings_save
    # distinguishes "absent" from "explicitly empty" on that basis, so None here is
    # load-bearing, not a convenience.
    observation_log_config: Optional[dict] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
