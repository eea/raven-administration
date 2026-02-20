from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class AttainmentModel(RavenBaseModel):
    id: str
    name: str
    assessment_regime_id: str
    comment: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class GenerateModel(BaseModel):
    year: int
    deleteExistingAttainments: bool

    def __getitem__(self, key):
        return super().__getattribute__(key)
