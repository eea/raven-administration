from pydantic import BaseModel
from typing import Optional
from pytz import timezone
from typing import List
from core.base_model import RavenBaseModel


class LoggerLastValue(RavenBaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
