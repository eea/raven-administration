"""
Pydantic models for exceedances API endpoints.

These models validate request/response data for exceedances evaluation.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ExceedancesZoneModel(BaseModel):
    """Request model for zone exceedances evaluation."""
    zone_id: str = Field(..., description="Zone identifier")
    year: int = Field(..., ge=1990, le=2100, description="Year to evaluate")
    directive: str = Field(..., pattern="^(2008/50|2024/2881|WHO)$", description="Directive (2008/50, 2024/2881, or WHO)")
    pollutant: Optional[str] = Field(None, description="Optional pollutant filter (e.g., NO2, PM10)")


class ExceedancesRegimeModel(BaseModel):
    """Request model for single assessment regime evaluation."""
    regime_id: str = Field(..., description="Assessment regime identifier")
    year: int = Field(..., ge=1990, le=2100, description="Year to evaluate")
    directive: str = Field(..., pattern="^(2008/50|2024/2881|WHO)$", description="Directive (2008/50, 2024/2881, or WHO)")
