"""
EEA-compliant ID generation for Plans & Programs integration.

This module provides functions to generate standardized IDs required by the
EEA Plans & Programs (H-K) module for compliance assessment and reporting.

IDs are generated on-demand (not stored in RAVEN database) to ensure:
- Consistency: same inputs always produce same IDs
- Stateless: no database writes needed
- Idempotent: can regenerate IDs reliably

Author: RAVEN Development Team
Date: January 30, 2026
"""

from typing import Optional


class EEAIDGenerator:
    """Generate EEA-compliant IDs for assessment regimes, compliance, etc."""
    
    @staticmethod
    def generate_assessment_regime_id(
        country_code: str,
        zone_code: str,
        pollutant: str,
        year: int
    ) -> str:
        """
        Generate assessmentregimeid following EEA naming convention.
        
        Format: {COUNTRY}_REGIME_{ZONE}_{POLLUTANT}_{YEAR}
        
        Args:
            country_code: ISO 2-letter country code (e.g., 'AD', 'NO')
            zone_code: Zone identifier or name (e.g., 'Escaldes-Engordany', 'OSLO')
            pollutant: Pollutant notation (e.g., 'NO2', 'PM10')
            year: Reporting year (e.g., 2024)
        
        Returns:
            Assessment regime ID string
        
        Example:
            >>> EEAIDGenerator.generate_assessment_regime_id('AD', 'Escaldes-Engordany', 'NO2', 2024)
            'AD_REGIME_ESCALDES_NO2_2024'
        """
        # Clean zone name: extract first part before hyphen, limit to 20 chars
        zone_clean = zone_code.split('-')[0].upper().strip()[:20]
        return f"{country_code.upper()}_REGIME_{zone_clean}_{pollutant.upper()}_{year}"
    
    @staticmethod
    def generate_compliance_id(
        country_code: str,
        year: int,
        sequence: int
    ) -> str:
        """
        Generate complianceid for a specific exceedance instance.
        
        Format: {COUNTRY}_COMP_{YEAR}_{SEQ}
        
        Args:
            country_code: ISO 2-letter country code
            year: Reporting year
            sequence: Sequential number for this year (1-based)
        
        Returns:
            Compliance ID string with 3-digit padded sequence
        
        Example:
            >>> EEAIDGenerator.generate_compliance_id('AD', 2024, 5)
            'AD_COMP_2024_005'
        """
        return f"{country_code.upper()}_COMP_{year}_{sequence:03d}"
    
    @staticmethod
    def generate_assessment_method_id(
        country_code: str,
        zone_code: str,
        pollutant: str,
        sequence: int
    ) -> str:
        """
        Generate assessmentmethodid for a measurement method.
        
        Format: {COUNTRY}_METHOD_{ZONE}_{POLLUTANT}_{SEQ}
        
        Args:
            country_code: ISO 2-letter country code
            zone_code: Zone identifier or name
            pollutant: Pollutant notation
            sequence: Sequential number (1-based)
        
        Returns:
            Assessment method ID string with 3-digit padded sequence
        
        Example:
            >>> EEAIDGenerator.generate_assessment_method_id('AD', 'Escaldes', 'NO2', 1)
            'AD_METHOD_ESCALDES_NO2_001'
        """
        zone_clean = zone_code.split('-')[0].upper().strip()[:20]
        return f"{country_code.upper()}_METHOD_{zone_clean}_{pollutant.upper()}_{sequence:03d}"
    
    @staticmethod
    def generate_attainment_id(
        country_code: str,
        year: int,
        zone_code: str,
        pollutant: str
    ) -> str:
        """
        Generate attainmentid linking to Flow G attainment status.
        
        Format: ATT_{COUNTRY}_{YEAR}_{ZONE}_{POLLUTANT}
        
        Args:
            country_code: ISO 2-letter country code
            year: Reporting year
            zone_code: Zone identifier or name
            pollutant: Pollutant notation
        
        Returns:
            Attainment ID string
        
        Example:
            >>> EEAIDGenerator.generate_attainment_id('AD', 2024, 'Escaldes', 'NO2')
            'ATT_AD_2024_ESCALDES_NO2'
        """
        zone_clean = zone_code.split('-')[0].upper().strip()[:20]
        return f"ATT_{country_code.upper()}_{year}_{zone_clean}_{pollutant.upper()}"
    
    @staticmethod
    def generate_sr_id(sampling_point_code: str) -> str:
        """
        Generate sampling reference ID (sr_id).
        
        For RAVEN, we use the existing sampling point ID directly.
        
        Args:
            sampling_point_code: Existing sampling point ID from RAVEN
        
        Returns:
            Sampling reference ID (same as input)
        
        Example:
            >>> EEAIDGenerator.generate_sr_id('SPO-AD0940A-0005')
            'SPO-AD0940A-0005'
        """
        return sampling_point_code


def get_country_code_from_settings(cursor) -> Optional[str]:
    """
    Extract country code from settings.namespace field.
    
    RAVEN instances are single-tenant per country. The country code is stored
    in the settings.namespace field following the pattern:
    "{COUNTRY_CODE}.{Organization}.{Domain}"
    
    Args:
        cursor: Database cursor (psycopg2)
        
    Returns:
        2-letter country code (uppercase) or None if not found
    
    Example:
        >>> # settings.namespace = "AD.GovernAndorra.AQ"
        >>> get_country_code_from_settings(cursor)
        'AD'
    
    Raises:
        None - returns None if settings table is empty or namespace is invalid
    """
    try:
        cursor.execute("SELECT namespace FROM settings LIMIT 1")
        row = cursor.fetchone()
        
        if row and row['namespace']:
            # Extract first part before dot: "AD.GovernAndorra.AQ" -> "AD"
            namespace = str(row['namespace'])
            parts = namespace.split('.')
            if len(parts) > 0 and len(parts[0]) >= 2:
                country_code = parts[0].upper()
                return country_code
        
        return None
    except Exception:
        # Fail gracefully if settings table doesn't exist or other DB error
        return None


def validate_country_code(cursor, requested_code: Optional[str] = None) -> str:
    """
    Get and validate country code against database settings.
    
    If a country code is requested, validates it matches the database.
    If no code is requested, extracts it from database settings.
    
    Args:
        cursor: Database cursor
        requested_code: Optional country code from API request
        
    Returns:
        Validated 2-letter country code (uppercase)
        
    Raises:
        ValueError: If codes don't match or no country code available
    
    Example:
        >>> # Database has "AD.GovernAndorra.AQ"
        >>> validate_country_code(cursor, "AD")  # Valid
        'AD'
        >>> validate_country_code(cursor, "NO")  # Invalid
        ValueError: Country code mismatch...
        >>> validate_country_code(cursor)  # No request, use DB
        'AD'
    """
    db_country_code = get_country_code_from_settings(cursor)
    
    if requested_code:
        requested_upper = requested_code.upper()
        
        # Validate request matches database if DB has country code
        if db_country_code and requested_upper != db_country_code:
            raise ValueError(
                f"Country code mismatch: requested '{requested_upper}', "
                f"but this RAVEN instance is configured for '{db_country_code}' "
                f"(from settings.namespace)"
            )
        
        return requested_upper
    
    # No request - use database value
    if db_country_code:
        return db_country_code
    
    # No code in request or database
    raise ValueError(
        "Country code not found in settings.namespace and not provided in request. "
        "Please ensure settings table is configured or provide countrycode parameter."
    )


# Convenience function for common use case
def get_or_validate_country_code(cursor, requested_code: Optional[str] = None) -> str:
    """
    Alias for validate_country_code - preferred name for clarity.
    
    Gets country code from settings if not provided, or validates
    that provided code matches settings.
    
    Args:
        cursor: Database cursor
        requested_code: Optional country code from API request
        
    Returns:
        Validated 2-letter country code (uppercase)
    """
    return validate_country_code(cursor, requested_code)
