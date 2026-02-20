"""
EEA module for Plans & Programs integration.

This package provides utilities for generating EEA-compliant IDs and
formatting data for integration with the Plans & Programs (H-K) module.
"""

from .id_generator import (
    EEAIDGenerator,
    get_country_code_from_settings,
    validate_country_code,
    get_or_validate_country_code
)

__all__ = [
    'EEAIDGenerator',
    'get_country_code_from_settings',
    'validate_country_code',
    'get_or_validate_country_code'
]
