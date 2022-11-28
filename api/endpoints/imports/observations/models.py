from pydantic import BaseModel
from typing import Optional
from pytz import timezone
from typing import List


class LoggerLastValue(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
