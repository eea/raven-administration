"""AQR3 v5.02 identifier construction and validation.

Four identifier formats are **fully mandatory** in AQR3 v5.02 (see the reporting
guide's `Identifiers` sheet) and two are partially mandatory. Reportnet3 rejects
a submission whose identifiers do not match, so these are generated from a single
place and validated before write rather than discovered by the EEA's QC.

    AssessmentRegimeId  ARE_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ClassificationYear>_<idx>
    AttainmentId        ATT_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<ReportingYear>_<idx>
    ScenarioId          SCE_<ZoneId>_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>_<idx>
    SamplingPointRef    SPOref_<StationEoICode>_<PollutantId>_<idx>
    AssessmentMethodId  MOD_<specific> | OBE_<specific>          (models only)
    PlanId              PLA_<ZoneId>[_<PollutantId>_<ObjectiveType>_<ProtectionTarget>_<ReportingMetric>]

The separator must be an underscore for the fully mandatory ones. Everything is
derived from its inputs, so regenerating always yields the same identifier.

The pre-v5.02 formats this replaced (`AD_REGIME_ESCALDES_NO2_2024`,
`ATT_AD_2024_ESCALDES_NO2`, `AD_COMP_2024_005`) were all non-conformant, and the
`complianceid` concept is gone: CAM keys on AttainmentId.
"""
import re
from typing import Optional

SEP = '_'

# Reportnet3 identifier column widths (varchar(50) for the regime/attainment ids,
# varchar(32) for SamplingPointReferenceId).
MAX_LEN = {'ARE': 50, 'ATT': 50, 'SCE': 50, 'PLA': 50, 'SPOref': 32, 'MOD': 50, 'OBE': 50}


class IdentifierError(ValueError):
    """An identifier does not match its mandatory AQR3 format."""


def _part(value, what):
    """Normalise one identifier segment and reject an embedded separator."""
    if value is None or str(value).strip() == '':
        raise IdentifierError(f'{what} is required to build the identifier')
    text = str(value).strip()
    if SEP in text:
        raise IdentifierError(
            f'{what} ({text!r}) contains "{SEP}", which is the mandatory AQR3 separator')
    return text


class EEAIDGenerator:
    """Build the AQR3 v5.02 mandatory-format identifiers."""

    @staticmethod
    def generate_assessment_regime_id(zone_id, pollutant_id, objective_type,
                                      protection_target, reporting_metric,
                                      classification_year, index=1) -> str:
        """AQR3 ARZ_02 AssessmentRegimeId.

        >>> EEAIDGenerator.generate_assessment_regime_id(
        ...     'ZON_DU000A', 5, 'LV', 'H', 'aMean', 2021, 1)
        'ARE_ZON_DU000A_0005_LV_H_aMean_2021_1'
        """
        return SEP.join([
            'ARE',
            str(zone_id).strip(),           # ZoneIds themselves contain '_' (ZON_DU000A)
            f'{int(pollutant_id):04d}',
            _part(objective_type, 'ObjectiveType'),
            _part(protection_target, 'ProtectionTarget'),
            _part(reporting_metric, 'ReportingMetric'),
            str(int(classification_year)),
            str(index)[:1],                 # guide: max length 1
        ])

    @staticmethod
    def generate_attainment_id(zone_id, pollutant_id, objective_type,
                               protection_target, reporting_metric,
                               reporting_year, index=1) -> str:
        """AQR3 CAM_15 AttainmentId.

        >>> EEAIDGenerator.generate_attainment_id(
        ...     'ZON_DU000A', 5, 'LV', 'H', 'daysAbove', 2024, 1)
        'ATT_ZON_DU000A_0005_LV_H_daysAbove_2024_1'
        """
        return SEP.join([
            'ATT',
            str(zone_id).strip(),
            f'{int(pollutant_id):04d}',
            _part(objective_type, 'ObjectiveType'),
            _part(protection_target, 'ProtectionTarget'),
            _part(reporting_metric, 'ReportingMetric'),
            str(int(reporting_year)),
            str(int(index)),                # guide: max length 2, numeric
        ])

    @staticmethod
    def generate_scenario_id(zone_id, pollutant_id, objective_type,
                             protection_target, reporting_metric, index=1) -> str:
        """AQR3 CPL_04 ScenarioId. Owned by raven-plan-program; here for validation."""
        return SEP.join([
            'SCE',
            str(zone_id).strip(),
            f'{int(pollutant_id):04d}',
            _part(objective_type, 'ObjectiveType'),
            _part(protection_target, 'ProtectionTarget'),
            _part(reporting_metric, 'ReportingMetric'),
            str(int(index)),
        ])

    @staticmethod
    def generate_plan_id(zone_id, pollutant_id=None, objective_type=None,
                         protection_target=None, reporting_metric=None) -> str:
        """AQR3 CPL_03 PlanId. Only the PLA prefix is mandatory; the rest is
        recommended and included only where the plan is specific to it."""
        parts = ['PLA', str(zone_id).strip()]
        if pollutant_id is not None:
            parts.append(f'{int(pollutant_id):04d}')
        for value in (objective_type, protection_target, reporting_metric):
            if value:
                parts.append(str(value).strip())
        return SEP.join(parts)

    @staticmethod
    def generate_sampling_point_reference_id(station_eoi_code, pollutant_id, index=1) -> str:
        """AQR3 SPO_03 SamplingPointReferenceId.

        >>> EEAIDGenerator.generate_sampling_point_reference_id('DU0001', 5, 1)
        'SPOref_DU0001_0005_1'
        """
        identifier = SEP.join([
            'SPOref',
            _part(station_eoi_code, 'StationEoICode'),
            f'{int(pollutant_id):04d}',
            str(int(index))[:2],            # guide: max length 2
        ])
        if len(identifier) > MAX_LEN['SPOref']:
            raise IdentifierError(
                f'SamplingPointReferenceId {identifier!r} exceeds '
                f'{MAX_LEN["SPOref"]} characters (SPO_03 is varchar(32))')
        return identifier

    @staticmethod
    def generate_model_assessment_method_id(kind, specific) -> str:
        """AQR3 MOE_02 AssessmentMethodId for a model or objective estimation.

        >>> EEAIDGenerator.generate_model_assessment_method_id('MOD', 'DU_NO2')
        'MOD_DU_NO2'
        """
        prefix = str(kind).strip().upper()
        if prefix not in ('MOD', 'OBE'):
            raise IdentifierError(
                f'Model AssessmentMethodId must start with MOD or OBE, got {kind!r}')
        if not str(specific).strip():
            raise IdentifierError('A specific identifier is required after the MOD/OBE prefix')
        return f'{prefix}{SEP}{str(specific).strip()}'


# ---------------------------------------------------------------------------
# Validation
#
# Applied at write time so a malformed identifier is rejected here rather than by
# Reportnet3's QC after submission.
# ---------------------------------------------------------------------------

_YEAR = r'(?:19|20)\d{2}'
_CODE = r'[A-Za-z0-9.+-]+'

PATTERNS = {
    # ZoneId may itself contain underscores, so it is matched non-greedily and the
    # tail is pinned by the fixed-shape trailing segments.
    'AssessmentRegimeId':
        re.compile(rf'^ARE_(?P<zone>.+?)_(?P<pollutant>\d+)_(?P<objective>{_CODE})'
                   rf'_(?P<target>{_CODE})_(?P<metric>{_CODE})_(?P<year>{_YEAR})_(?P<idx>\w)$'),
    'AttainmentId':
        re.compile(rf'^ATT_(?P<zone>.+?)_(?P<pollutant>\d+)_(?P<objective>{_CODE})'
                   rf'_(?P<target>{_CODE})_(?P<metric>{_CODE})_(?P<year>{_YEAR})_(?P<idx>\d{{1,2}})$'),
    'ScenarioId':
        re.compile(rf'^SCE_(?P<zone>.+?)_(?P<pollutant>\d+)_(?P<objective>{_CODE})'
                   rf'_(?P<target>{_CODE})_(?P<metric>{_CODE})_(?P<idx>\d{{1,2}})$'),
    'SamplingPointReferenceId':
        re.compile(rf'^SPOref_(?P<station>{_CODE})_(?P<pollutant>\d+)_(?P<idx>\d{{1,2}})$'),
    'PlanId':
        re.compile(r'^PLA_.+$'),
    'ModelAssessmentMethodId':
        re.compile(r'^(?:MOD|OBE)_.+$'),
}


def validate_identifier(kind, value, required=True):
    """Check `value` against the mandatory AQR3 format for `kind`.

    Returns the value unchanged so it can be used inline. Raises IdentifierError
    with the expected shape when it does not match.
    """
    if value in (None, ''):
        if required:
            raise IdentifierError(f'{kind} is required')
        return value

    pattern = PATTERNS.get(kind)
    if pattern is None:
        raise IdentifierError(f'No AQR3 format defined for {kind!r}')

    if not pattern.match(str(value)):
        raise IdentifierError(
            f'{kind} {value!r} does not match its mandatory AQR3 v5.02 format. '
            f'Expected {pattern.pattern}')

    limit = MAX_LEN.get(str(value).split(SEP)[0])
    if limit and len(str(value)) > limit:
        raise IdentifierError(f'{kind} {value!r} exceeds {limit} characters')

    return value


def is_valid_identifier(kind, value):
    """Non-raising form of validate_identifier."""
    try:
        validate_identifier(kind, value)
        return True
    except IdentifierError:
        return False


def get_country_code_from_settings(cursor) -> Optional[str]:
    """
    Extract country code from settings table.
    
    RAVEN v4 instances are single-tenant per country.
    Country code is a FK in settings.country_code_id -> eea_countries.id
    
    Args:
        cursor: Database cursor (psycopg2)
        
    Returns:
        2-letter country code (uppercase) or None if not found
    
    Example:
        >>> # settings.country_code_id = 'AD' (FK to eea_countries)
        >>> get_country_code_from_settings(cursor)
        'AD'
    
    Raises:
        None - returns None if settings table is empty or cannot be read
    """
    try:
        cursor.execute("""
            SELECT s.country_code_id, c.notation 
            FROM settings s
            LEFT JOIN eea_countries c ON s.country_code_id = c.id
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            # notation from joined eea_countries table
            notation = row.get('notation') if hasattr(row, 'get') else (row[1] if len(row) > 1 else None)
            if notation:
                return notation.upper()
            # Fallback: country_code_id itself might be the code (e.g., 'NO')
            country_code_id = row.get('country_code_id') if hasattr(row, 'get') else row[0]
            if country_code_id:
                return str(country_code_id).upper()
        
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
