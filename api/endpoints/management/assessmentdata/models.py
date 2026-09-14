"""Assessment data: which methods assess which assessment regime.

Not an AQR3 table of its own. It is the junction AQR3 CAM is derived from --
core/data/plans_programs_export.py walks it to find the methods assessing each
regime -- so what it can express decides what Raven can report.

`assessmentlocal_id` is generated in the database from `sampling_point_id` and
`model_id`, so it is read back but never written: AQR3 CAM_05 AssessmentMethodId is
either a sampling point or a model, and exactly one of the two is set.

`from_time` / `to_time` bound the period the method assessed the regime, mirroring
`sampling_points`. Both NULL means unbounded, which is what every link written before
4.502.24 carries. Close a link rather than deleting it: recalculating an earlier
reporting year then still reproduces what was submitted for it.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class AssessmentDataModel(RavenBaseModel):
    # Optional on the way in: the insert route derives one, because this id is not an
    # AQR3 identifier and there is nothing useful for a person to type.
    id: Optional[str] = None
    assessment_regime_id: str
    sampling_point_id: Optional[str] = None     # CAM_05, by measurement
    model_id: Optional[str] = None              # CAM_05, by model / objective estimation
    assessmenttype: str                         # CAM_07
    assessmentmethodedescription: Optional[str] = None
    from_time: Optional[str] = None
    to_time: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
