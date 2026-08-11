from typing import Optional

from core.base_model import RavenBaseModel


class ModelObjectiveEstimationModel(RavenBaseModel):
    """AQR3 MOE ModelObjectiveEstimation.

    `id` is the AssessmentMethodId and must carry the mandatory MOD_ or OBE_
    prefix; the route validates it via core.eea.id_generator.
    """
    id: str
    data_aggregation_process_id: str
    assessment_method_name: Optional[str] = None
    pollutant_id: Optional[int] = None
    result_encoding_id: Optional[str] = None
    method_application_id: Optional[str] = None
    generic_mqi: Optional[float] = None
    data_quality_document_id: Optional[str] = None
    method_document_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
