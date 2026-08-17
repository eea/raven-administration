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


class ExternalResultKey(RavenBaseModel):
    """Identifies an existing MRE row. All three parts are the AQR3 key."""
    assessment_method_id: str
    start_time: str
    data_aggregation_process_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class ExternalResultModel(RavenBaseModel):
    """AQR3 MRE MOEResultExternal — gridded results supplied as a GeoTIFF.

    The same shape as MRI minus x/y/value, plus the attachment: where MRI holds a
    value per grid cell, MRE says "the values are in this file", which the country
    uploads to Reportnet3 itself. So there is one row per timestep, not per cell.
    """
    assessment_method_id: str                        # MRE_02
    start_time: str                                  # MRE_03
    data_aggregation_process_id: str                 # MRE_04
    pollutant_id: Optional[int] = None               # MRE_05
    end_time: Optional[str] = None                   # MRE_06
    unit_id: Optional[str] = None                    # MRE_07
    validity_id: Optional[int] = None                # MRE_08
    spatial_resolution: Optional[int] = None         # MRE_09
    # MRE_11 — the filename of the GeoTIFF uploaded to Reportnet3, validated by
    # core.reporting.aqr3.attachments. MRE_10 ResultTime is set to now() on write.
    geotiff_attachment: Optional[str] = None

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
