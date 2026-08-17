"""AQR3 ARZ AssessmentRegimeZone.

An assessment regime is the combination a country assesses compliance against:
a zone, a pollutant, an objective type, a protection target and a reporting
metric, for a classification year. Compliance (CAM) is derived from these, so
without them a deployment can report neither ARZ nor CAM.

`id` is AQR3 ARZ_02 and carries a mandatory format:
ARE_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ClassificationYear>_<idx>
A supplied id is validated against it; an omitted one is derived from the other
fields. Both go through core.eea.id_generator.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class AssessmentRegimeModel(RavenBaseModel):
    # Optional on the way in: left empty, the insert route derives a conformant id
    # from the parts below rather than making someone type a seven-segment string.
    id: Optional[str] = None                            # ARZ_02
    zone_id: Optional[str] = None                       # ARZ_03
    pollutant_id: int                                   # ARZ_09, NOT NULL in the schema
    protection_target_id: Optional[str] = None          # ARZ_10
    objective_type_id: Optional[str] = None             # ARZ_11
    reporting_metric_id: Optional[str] = None           # ARZ_12
    assessment_threshold_exceedance_id: Optional[str] = None   # ARZ_13
    postponement_year: Optional[int] = None             # ARZ_14
    fixed_measurement_reduction: Optional[bool] = False  # ARZ_15
    zone_resident_population_year: Optional[int] = None  # ARZ_16
    zone_resident_population: Optional[int] = None      # ARZ_17
    classification_year: Optional[int] = None           # ARZ_18
    classification_document_id: Optional[str] = None    # ARZ_19

    def __getitem__(self, key):
        return super().__getattribute__(key)
