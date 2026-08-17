"""AQR3 ADJ PollutionLevelAdjustment.

Deductions from measured pollution levels for causes outside a country's control —
natural sources and winter road salting/sanding. Under the AAQD a country may
subtract these before judging compliance against a limit value, so each row is the
audit trail for a deduction that can change whether a zone passes or fails:
*for this attainment*, *this much was deducted for this cause*, *quantified by this
model*, *and here is the report justifying it*.

The AQR3 key is (CountryCode, AttainmentId, AdjustmentSource), so attainment_id
and adjustment_source_id together identify a row. Both are part of the key and
editable, hence the separate key/values shape on update.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class AdjustmentKey(RavenBaseModel):
    """Identifies an existing adjustment."""
    attainment_id: str
    adjustment_source_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class AdjustmentModel(RavenBaseModel):
    attainment_id: str                                       # ADJ_02
    adjustment_source_id: str                                # ADJ_03
    # ADJ_04. The guide requires a different method per AdjustmentSource, so that
    # the deducted amounts can be reported per source in the MOEResult tables.
    adjustment_assessment_method_id: Optional[str] = None
    # ADJ_05. The guide gives this attribute no Content, no SQL type and no
    # ReportNet3 type — an EEA omission. Every other *DocumentId in v5.02 is a
    # reference into the Documentation table, and the column has an FK to
    # documents, so it is modelled that way.
    adjustment_document_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
