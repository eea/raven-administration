"""AQR3 CAM ComplianceAssessmentMethod models.

The row set is derived, so the key is not editable; only the columns the evaluation
does not yet compute are. The key therefore travels separately from the values, to
address the row rather than to be rewritten.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class ComplianceKey(RavenBaseModel):
    """Identifies an existing compliance row — the AQR3 CAM primary key."""
    reporting_year: int
    assessment_regime_id: str
    data_aggregation_process_id: str
    assessment_method_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class ComplianceValues(RavenBaseModel):
    """The columns an operator maintains, all optional.

    Every one is legitimately blank: these are what
    core/data/plans_programs_export.py still supplies as TODO placeholders, so a row
    starts empty and is filled in as the figures become known. `deletion` (CAM_18) and
    `attainment_index` (CAM_15's ordering index) are never computed at all -- the first
    is AQR3's retraction flag, the second is how an operator says a regime holds more
    than one compliance situation. `srs_id` is not computable either.
    """
    is_exceedance: Optional[bool] = None
    data_coverage: Optional[float] = None
    pollution_level: Optional[float] = None
    pollution_level_adjusted: Optional[float] = None
    relative_uncertainty_limit: Optional[float] = None
    assessment_mqi: Optional[float] = None
    correction_flag: Optional[bool] = None
    preliminary_reason_id: Optional[str] = None
    # CAM_16. Not a figure the evaluation will ever supply: SRS_02 names a spatial area
    # an operator uploads, and SRS_06 points from that area at the model which assessed
    # it, so the link only exists if somebody makes it.
    srs_id: Optional[str] = None
    # CAM_15's trailing ordering index. NOT NULL with a default of 1 in the database, so
    # the route coerces a cleared field back to 1 rather than writing NULL. Raising it
    # splits one assessment regime into more than one compliance situation.
    attainment_index: Optional[int] = None
    deletion: Optional[bool] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
