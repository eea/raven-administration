from core.base_model import RavenBaseModel
from typing import Optional


class ProcessModel(RavenBaseModel):
    id: str
    activity_begin: str
    activity_end: Optional[str] = None
    data_quality_report_id: str
    equivalence_demonstration_report_id: str
    process_documentation_id: str
    measurement_type_id: str
    method_id: str
    equipment_id: str
    analytical_technique_id: str
    equivalence_demonstrated_id: str
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
