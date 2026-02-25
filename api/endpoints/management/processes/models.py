from core.base_model import RavenBaseModel
from typing import Optional


class ProcessModel(RavenBaseModel):
    id: str
    activity_begin: str
    activity_end: Optional[str] = None
    data_quality_report_id: Optional[str] = None
    equivalence_demonstration_report_id: Optional[str] = None
    process_documentation_id: Optional[str] = None
    measurement_type_id: Optional[str] = None
    method_id: Optional[str] = None
    equipment_id: Optional[str] = None
    analytical_technique_id: Optional[str] = None
    equivalence_demonstrated_id: Optional[str] = None
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
