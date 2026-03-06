"""
Pydantic models for Documents
"""
from pydantic import BaseModel, Field


class DocumentModel(BaseModel):
    """Model for document metadata"""
    id: str = Field(..., min_length=1, max_length=255)
    datatable_id: str = Field(..., min_length=1, max_length=50)
    documentobject_id: str = Field(..., min_length=1, max_length=50)
    documentattachment: str = Field(..., min_length=1, max_length=500)
