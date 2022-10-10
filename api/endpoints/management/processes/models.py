from datetime import datetime
from pydantic import BaseModel

# select id, measurement_type, measurement_method, other_measurement_method, sampling_method, other_sampling_method, analytical_tech, other_analytical_tech, sampling_equipment, measurement_equipment, equiv_demonstration, equiv_demonstration_report, detection_limit, detection_limit_uom, uncertainty_estimate, documentation, qa_report, duration_number, duration_unit, cadence_number, cadence_unit, responsible_authority_id, other_measurement_equipment, other_sampling_equipment from processes


class ProcessModel(BaseModel):
    id: str
    measurement_type: str
    measurement_type_name: str
    measurement_method: str
    measurement_method_name: str
    other_measurement_method: str
    sampling_method: str
    other_sampling_method: str
    analytical_tech: str
    other_analytical_tech: str
    sampling_equipment: str
    measurement_equipment: str
    measurement_equipment_name: str
    equiv_demonstration: str
    equiv_demonstration_name: str
    equiv_demonstration_report: str
    detection_limit: int
    detection_limit_uom: str
    detection_limit_uom_name: str
    uncertainty_estimate: int
    documentation: str
    qa_report: str
    duration_number: int
    duration_unit: str
    duration_unit_name: str
    cadence_number: int
    cadence_unit: str
    cadence_unit_name: str
    responsible_authority_id: str
    responsible_authority: str
    other_measurement_equipment: str
    other_sampling_equipment: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
