"""
Pydantic models for Documents
"""
from typing import Optional

from pydantic import BaseModel, Field


class DocumentModel(BaseModel):
    """Model for document metadata"""
    id: str = Field(..., min_length=1, max_length=255)
    datatable_id: str = Field(..., min_length=1, max_length=50)
    documentobject_id: str = Field(..., min_length=1, max_length=50)
    # AQR3 DOC_06. Capped at the width the guide declares rather than truncated
    # on the way in: a silently shortened URL points somewhere else.
    document_original_url: Optional[str] = Field(None, max_length=100)
    # AQR3 DOC_05 — the filename of the PDF uploaded to Reportnet3 alongside the
    # CSVs. Raven records the reference, not the file. The route validates the
    # extension via core.reporting.aqr3.attachments.
    documentattachment: Optional[str] = Field(None, max_length=100)
