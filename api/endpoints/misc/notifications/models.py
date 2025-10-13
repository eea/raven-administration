from pydantic import BaseModel
from typing import Optional


class NotificationsModel(BaseModel):
    originalname: Optional[str]
    name: str
    emails: str
    enabled: bool
    sampling_points: Optional[list]

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    name: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
