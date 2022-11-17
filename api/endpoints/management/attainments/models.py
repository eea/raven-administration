from pydantic import BaseModel
from typing import Optional


class AttainmentModel(BaseModel):
    id: str
    name: str
    assessment_regime_id: str
    comment: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
