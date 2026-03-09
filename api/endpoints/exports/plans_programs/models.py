"""
Pydantic models for Plans & Programs exceedances export API.

These models define the request and response structure for the
/api/exports/exceedances/plans-and-programs endpoint.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional


class PlansAndProgramsExportRequest(BaseModel):
    """
    Request model for Plans & Programs exceedances export.
    
    This endpoint exports exceedances data formatted specifically for
    integration with the EEA Plans & Programs (Flow H-K) module.
    
    Example:
        {
            "reportingyear": 2024,
            "directive": "2024/2881",
            "pollutants": ["NO2", "PM10"],
            "exceedances_only": true
        }
    """
    
    countrycode: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=2,
        description=(
            "ISO 2-letter country code (e.g., 'NO', 'AD'). "
            "If not provided, will be extracted from settings.namespace. "
            "If provided, must match the RAVEN instance country."
        )
    )
    
    reportingyear: int = Field(
        ...,
        ge=2000,
        le=2100,
        description="Reporting year for which to export exceedances"
    )
    
    directive: str = Field(
        default="2024/2881",
        description=(
            "EU Air Quality Directive to evaluate against. "
            "Supported: '2008/50', '2024/2881', 'WHO'"
        )
    )
    
    pollutants: List[str] = Field(
        default=[],
        description=(
            "Filter by pollutant notations (e.g., ['NO2', 'PM10']). "
            "Empty list = all pollutants"
        )
    )
    
    zones: List[str] = Field(
        default=[],
        description=(
            "Filter by zone IDs (e.g., ['AD-ZONE-001']). "
            "Empty list = all zones"
        )
    )
    
    exceedances_only: bool = Field(
        default=True,
        description=(
            "If true, only return sampling points where thresholds were exceeded. "
            "If false, return all evaluated sampling points."
        )
    )
    
    assessment_types: List[str] = Field(
        default=[],
        description=(
            "Filter by assessment types (e.g., ['fixed', 'indicative', 'modelling']). "
            "Empty list = all types"
        )
    )
    
    @validator('countrycode')
    def validate_country_code(cls, v):
        """Validate and normalize country code."""
        if v is None:
            return None  # Will use settings.namespace
        
        # Normalize to uppercase
        v = v.upper().strip()
        
        # Validate length
        if len(v) != 2:
            raise ValueError(
                "Country code must be exactly 2 letters (ISO 3166-1 alpha-2)"
            )
        
        # Validate characters (A-Z only)
        if not v.isalpha():
            raise ValueError(
                "Country code must contain only letters (A-Z)"
            )
        
        return v
    
    @validator('pollutants')
    def normalize_pollutants(cls, v):
        """Normalize pollutant notations to uppercase."""
        return [p.upper().strip() for p in v if p]
    
    @validator('directive')
    def validate_directive(cls, v):
        """Validate directive format."""
        valid_directives = ['2008/50', '2024/2881', 'WHO']
        if v not in valid_directives:
            raise ValueError(
                f"Invalid directive '{v}'. Must be one of: {', '.join(valid_directives)}"
            )
        return v
    
    @validator('assessment_types')
    def normalize_assessment_types(cls, v):
        """Normalize and validate assessment types."""
        valid_types = ['fixed', 'indicative', 'modelling']
        normalized = []
        
        for t in v:
            t_lower = t.lower().strip()
            if t_lower not in valid_types:
                raise ValueError(
                    f"Invalid assessment type '{t}'. "
                    f"Must be one of: {', '.join(valid_types)}"
                )
            normalized.append(t_lower)
        
        return normalized
    
    class Config:
        json_schema_extra = {
            "example": {
                "countrycode": "NO",
                "reportingyear": 2024,
                "directive": "2024/2881",
                "pollutants": ["NO2", "PM10"],
                "zones": [],
                "exceedances_only": True,
                "assessment_types": []
            }
        }
