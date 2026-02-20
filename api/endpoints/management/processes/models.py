from pydantic import BaseModel
from typing import Optional
from core.base_model import RavenBaseModel


class ProcessModel(RavenBaseModel):
    id: str
    measurement_type_id: str
    measurement_method_id: str
    equiv_demonstration_id: str
    detection_limit: float
    detection_limit_uom_id: str
    duration_number: int
    duration_unit_id: str
    cadence_number: int
    cadence_unit_id: str
    authority_id: str

    measurement_equipment_id: Optional[str] = None
    other_measurement_equipment: Optional[str] = None
    other_measurement_method: Optional[str] = None
    analytical_tech: Optional[str] = None
    other_analytical_tech: Optional[str] = None
    sampling_equipment: Optional[str] = None
    other_sampling_equipment: Optional[str] = None
    equiv_demonstration_report: Optional[str] = None
    uncertainty_estimate: Optional[float] = None
    documentation: Optional[str] = None
    qa_report: Optional[str] = None

    sampling_method: Optional[str] = None
    other_sampling_method: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
