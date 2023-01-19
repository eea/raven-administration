from pydantic import BaseModel
from typing import List


class AssessmentRegimeDataModel(BaseModel):
    assessment_regime_id: str
    sampling_point_id: str
    assessment_type_id: str
    description: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class AssessmentRegimeModel(BaseModel):
    id: str
    name: str
    object_type_id: str
    reporting_metric_id: str
    protection_target_id: str
    include: bool
    year: int
    report: str
    zone_id: str
    pollutant_id: str
    exceedance_id: str
    data: List[AssessmentRegimeDataModel]

    def __getitem__(self, key):
        return super().__getattribute__(key)
