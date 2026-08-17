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


class ModelResultUploadModel(RavenBaseModel):
    """AQR3 MRI MOEResultInline — the metadata accompanying a gridded upload.

    The values come from a multipart form rather than JSON, so everything arrives
    as a string and is coerced here. Declared as a model rather than validated by
    hand so the required fields, and the columns each one writes, are stated in
    one place.

    Not included, because neither is a user's to choose:
      * x / y  — snapped to the EPSG:3035 INSPIRE grid from the raster (MRI_05/06)
      * result_time — now() at write (MRI_13)
    """
    assessment_method_id: str                        # MRI_02, the model being loaded
    start_time: str                                  # MRI_03
    data_aggregation_process_id: str                 # MRI_04
    end_time: Optional[str] = None                   # MRI_08
    pollutant_id: Optional[int] = None               # MRI_07
    value: Optional[float] = None                    # MRI_09, per raster pixel
    unit_id: Optional[str] = None                    # MRI_10
    validity_id: Optional[int] = None                # MRI_11
    spatial_resolution: Optional[int] = None         # MRI_12

    def __getitem__(self, key):
        return super().__getattribute__(key)
