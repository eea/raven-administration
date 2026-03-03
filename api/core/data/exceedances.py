"""
Air Quality Exceedances Evaluation

This module evaluates whether air quality statistics exceed regulatory thresholds
defined in EU Air Quality Directives (2008/50/EC, 2024/2881) and WHO guidelines.

Key Concepts:
- Aggregations (Statistics): Calculate statistical values from observations
- Thresholds: Regulatory limits defined in directives
- Exceedances: When aggregation values breach thresholds

Architecture:
- Reuses existing Statistics class for all aggregation calculations
- Stores directive thresholds as Python constants (not in database)
- Evaluates per assessment regime (zone + pollutant + objective type)
"""

from typing import Dict, List, Optional, Any
from core.data.statistics import Statistics


# ============================================================================
# DIRECTIVE THRESHOLDS
# Parsed from docs-nilu/aggregations and statistics/Exceedances_Raven.csv
# ============================================================================

DIRECTIVE_THRESHOLDS = {
    # PM10 Thresholds
    "PM10": {
        "LV": {  # Limit Value
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 40, "operator": ">"},
                "2024/2881": {"value": 20, "operator": ">"},
                "WHO": {"value": 15, "operator": ">"}
            },
            "Daily LV (50)": {
                "statistic": "P1Y-daysAbove50",
                "unit": "days",
                "2008/50": {"value": 35, "operator": ">"},
                "comment": "LV: 50 µg/m³. Not to be exceeded on more than 35 days per year"
            },
            "Daily LV (45)": {
                "statistic": "P1Y-daysAbove45",
                "unit": "days",
                "2024/2881": {"value": 18, "operator": ">"}
            },
            "Daily LV (percentile)": {
                "statistic": "P1Y-P1D-per99",
                "unit": "µg/m³",
                "WHO": {"value": 45, "operator": ">"}
            }
        },
        "INT": {  # Information Threshold
            "Information threshold": {
                "statistic": "P1Y-daysAbove90",
                "unit": "days",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "ALT": {  # Alert Threshold
            "Alert threshold": {
                "statistic": "P1Y-3daysAbove90",
                "unit": "events",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        }
    },
    
    # PM2.5 Thresholds
    "PM2.5": {
        "LV": {
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 25, "operator": ">"},
                "2024/2881": {"value": 10, "operator": ">"},
                "WHO": {"value": 5, "operator": ">"}
            },
            "Daily LV (25)": {
                "statistic": "P1Y-daysAbove25",
                "unit": "days",
                "2024/2881": {"value": 18, "operator": ">"}
            },
            "Daily LV (percentile)": {
                "statistic": "P1Y-P1D-per99",
                "unit": "µg/m³",
                "WHO": {"value": 15, "operator": ">"}
            }
        },
        "INT": {
            "Information threshold": {
                "statistic": "P1Y-daysAbove50",
                "unit": "days",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "ALT": {
            "Alert threshold": {
                "statistic": "P1Y-3daysAbove50",
                "unit": "events",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        }
    },
    
    # NO2 Thresholds
    "NO2": {
        "LV": {
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 40, "operator": ">"},
                "2024/2881": {"value": 20, "operator": ">"},
                "WHO": {"value": 10, "operator": ">"}
            },
            "Hourly LV": {
                "statistic": "P1Y-hrsAbove200",
                "unit": "hours",
                "2008/50": {"value": 18, "operator": ">"},
                "2024/2881": {"value": 3, "operator": ">"},
                "WHO": {"value": 0, "operator": ">"},
                "comment": "LV: 200 µg/m³. Not to be exceeded on more than 18/3 hours per year"
            },
            "Daily LV (50)": {
                "statistic": "P1Y-daysAbove50",
                "unit": "days",
                "2024/2881": {"value": 18, "operator": ">"}
            },
            "Daily LV (percentile)": {
                "statistic": "P1Y-P1D-per99",
                "unit": "µg/m³",
                "WHO": {"value": 25, "operator": ">"}
            }
        },
        "INT": {
            "Information threshold": {
                "statistic": "P1Y-hrsAbove150",
                "unit": "hours",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "ALT": {
            "Alert threshold (400)": {
                "statistic": "P1Y-3hAbove400",
                "unit": "events",
                "2008/50": {"value": 0, "operator": ">"}
            },
            "Alert threshold (200)": {
                "statistic": "P1Y-3hAbove200",
                "unit": "events",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        }
    },
    
    # SO2 Thresholds
    "SO2": {
        "LV": {
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2024/2881": {"value": 20, "operator": ">"}
            },
            "Hourly LV": {
                "statistic": "P1Y-hrsAbove350",
                "unit": "hours",
                "2008/50": {"value": 24, "operator": ">"},
                "2024/2881": {"value": 3, "operator": ">"},
                "comment": "LV: 350 µg/m³. Not to be exceeded on more than 24/3 hours per year"
            },
            "Daily LV (125)": {
                "statistic": "P1Y-daysAbove125",
                "unit": "days",
                "2008/50": {"value": 3, "operator": ">"}
            },
            "Daily LV (50)": {
                "statistic": "P1Y-daysAbove50",
                "unit": "days",
                "2024/2881": {"value": 18, "operator": ">"}
            },
            "Daily LV (percentile)": {
                "statistic": "P1Y-P1D-per99",
                "unit": "µg/m³",
                "WHO": {"value": 40, "operator": ">"}
            }
        },
        "ALT": {
            "Alert threshold (350)": {
                "statistic": "P1Y-3hAbove350",
                "unit": "events",
                "2024/2881": {"value": 0, "operator": ">"}
            },
            "Alert threshold (500)": {
                "statistic": "P1Y-3hAbove500",
                "unit": "events",
                "2008/50": {"value": 0, "operator": ">"}
            }
        },
        "INT": {
            "Information threshold": {
                "statistic": "P1Y-hrsAbove275",
                "unit": "hours",
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "CL": {  # Critical Level
            "Critical level (annual)": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 20, "operator": ">"},
                "2024/2881": {"value": 20, "operator": ">"},
                "comment": "Vegetation protection: Annual mean"
            },
            "Critical level (winter)": {
                "statistic": "winter-avg",
                "unit": "µg/m³",
                "2008/50": {"value": 20, "operator": ">"},
                "2024/2881": {"value": 20, "operator": ">"},
                "comment": "Vegetation protection: Winter (Oct-Mar) mean"
            }
        }
    },
    
    # CO Thresholds
    "CO": {
        "LV": {
            "Maximum daily 8-hour mean": {
                "statistic": "P1Y-8hdmxAbove10",
                "unit": "days",
                "2008/50": {"value": 0, "operator": ">"},
                "2024/2881": {"value": 0, "operator": ">"},
                "WHO": {"value": 0, "operator": ">"}
            },
            "Daily LV (percentile)": {
                "statistic": "P1Y-P1D-per99",
                "unit": "mg/m³",
                "WHO": {"value": 4, "operator": ">"}
            },
            "Daily LV (4)": {
                "statistic": "P1Y-daysAbove4",
                "unit": "days",
                "2024/2881": {"value": 18, "operator": ">"}
            }
        }
    },
    
    # O3 Thresholds
    "O3": {
        "INT": {
            "Information threshold": {
                "statistic": "P1Y-hrsAbove180",
                "unit": "hours",
                "2008/50": {"value": 0, "operator": ">"},
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "ALT": {
            "Alert threshold": {
                "statistic": "P1Y-hrsAbove240",
                "unit": "hours",
                "2008/50": {"value": 0, "operator": ">"},
                "2024/2881": {"value": 0, "operator": ">"}
            }
        },
        "TV": {  # Target Value
            "TV Protection of vegetation": {
                "statistic": "AOT40c-P5Y",
                "unit": "µg/m³.h",
                "2008/50": {"value": 18000, "operator": ">"},
                "2024/2881": {"value": 18000, "operator": ">"}
            },
            "TV Protection of human health": {
                "statistic": "P3Y-dmaxAbove120",
                "unit": "days",
                "2008/50": {"value": 25, "operator": ">"},
                "2024/2881": {"value": 18, "operator": ">"}
            },
            "TV (percentile)": {
                "statistic": "P1Y-dmax-per99",
                "unit": "µg/m³",
                "WHO": {"value": 100, "operator": ">"}
            }
        },
        "LTO": {  # Long Term Objective
            "LTO Protection of human health (120)": {
                "statistic": "P1Y-dmaxAbove120",
                "unit": "days",
                "2008/50": {"value": 0, "operator": ">"}
            },
            "LTO Protection of human health (100)": {
                "statistic": "P1Y-dmaxAbove100",
                "unit": "days",
                "2024/2881": {"value": 3, "operator": ">"}
            },
            "LTO Protection of vegetation": {
                "statistic": "AOT40c",
                "unit": "µg/m³.h",
                "2008/50": {"value": 6000, "operator": ">"},
                "2024/2881": {"value": 6000, "operator": ">"}
            }
        }
    },
    
    # C6H6 (Benzene) Thresholds - Directive 2008/50/EC Annex II
    "C6H6": {
        "LV": {  # Limit Value
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 5, "operator": ">"},
                "comment": "Annual mean limit value: 5 µg/m³"
            }
        }
    },
    
    # Pb (Lead) Thresholds - Directive 2008/50/EC Annex II
    "Pb": {
        "LV": {  # Limit Value
            "Annual LV": {
                "statistic": "P1Y",
                "unit": "µg/m³",
                "2008/50": {"value": 0.5, "operator": ">"},
                "comment": "Annual mean limit value: 0.5 µg/m³"
            }
        }
    },
    
    # As (Arsenic) Thresholds - Directive 2008/50/EC Annex II
    "As": {
        "TV": {  # Target Value
            "Annual TV": {
                "statistic": "P1Y",
                "unit": "ng/m³",
                "2008/50": {"value": 6, "operator": ">"},
                "comment": "Annual mean target value: 6 ng/m³ (PM10 fraction)"
            }
        }
    },
    
    # Cd (Cadmium) Thresholds - Directive 2008/50/EC Annex II
    "Cd": {
        "TV": {  # Target Value
            "Annual TV": {
                "statistic": "P1Y",
                "unit": "ng/m³",
                "2008/50": {"value": 5, "operator": ">"},
                "comment": "Annual mean target value: 5 ng/m³ (PM10 fraction)"
            }
        }
    },
    
    # Ni (Nickel) Thresholds - Directive 2008/50/EC Annex II
    "Ni": {
        "TV": {  # Target Value
            "Annual TV": {
                "statistic": "P1Y",
                "unit": "ng/m³",
                "2008/50": {"value": 20, "operator": ">"},
                "comment": "Annual mean target value: 20 ng/m³ (PM10 fraction)"
            }
        }
    },
    
    # BaP (Benzo[a]pyrene) Thresholds - Directive 2008/50/EC Annex II
    "BaP": {
        "TV": {  # Target Value
            "Annual TV": {
                "statistic": "P1Y",
                "unit": "ng/m³",
                "2008/50": {"value": 1, "operator": ">"},
                "comment": "Annual mean target value: 1 ng/m³ (PM10 fraction)"
            }
        }
    }
}


# Pollutant URI mapping (for database queries)
POLLUTANT_URIS = {
    "NO2": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/8",
    "SO2": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/1",
    "O3": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/7",
    "PM10": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/5",
    "PM2.5": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6001",
    "CO": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/10",
    # Missing pollutants from P3 (Directive 2008/50/EC Annex II)
    "C6H6": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/20",  # Benzene
    "Pb": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/12",  # Lead (aerosol) - CORRECTED
    "As": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/18",  # Arsenic (aerosol) - CORRECTED
    "Cd": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/14",  # Cadmium (aerosol)
    "Ni": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/15",  # Nickel (aerosol) - CORRECTED
    "BaP": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/6015",  # Benzo(a)pyrene (air+aerosol) - CORRECTED
    "NOx": "http://dd.eionet.europa.eu/vocabulary/aq/pollutant/9"  # Nitrogen oxides
}

# Reverse mapping (URI to notation)
URI_TO_POLLUTANT = {v: k for k, v in POLLUTANT_URIS.items()}


# ============================================================================
# EXCEEDANCES CLASS
# ============================================================================

class Exceedances:
    """
    Evaluate air quality exceedances against directive thresholds.
    
    This class:
    1. Fetches assessment regimes from database (zone + pollutant + objective)
    2. Uses Statistics class to calculate aggregation values
    3. Compares values to directive thresholds
    4. Returns exceedance status and details
    """
    
    def __init__(self, cursor):
        """
        Initialize Exceedances evaluator.
        
        Args:
            cursor: Database cursor (psycopg2)
        """
        self.cursor = cursor
        self.statistics = Statistics(cursor)
    
    def get_zones(self, year: int) -> List[Dict[str, Any]]:
        """
        Get all zones for a specific year.
        
        Args:
            year: Year to filter zones
            
        Returns:
            List of zone dictionaries with id, name, code, population
        """
        self.cursor.execute("""
            SELECT id, name, code, population, area
            FROM zones
            WHERE year = %s
            ORDER BY name
        """, (year,))
        
        return self.cursor.fetchall()
    
    def get_assessment_regimes(self, zone_id: str, pollutant_notation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get assessment regimes for a zone, optionally filtered by pollutant.
        
        Args:
            zone_id: Zone identifier
            pollutant_notation: Optional pollutant notation (e.g., 'NO2', 'PM10')
            
        Returns:
            List of assessment regime dictionaries
        """
        if pollutant_notation:
            pollutant_uri = POLLUTANT_URIS.get(pollutant_notation)
            if not pollutant_uri:
                raise ValueError(f"Unknown pollutant: {pollutant_notation}")
            
            self.cursor.execute("""
                SELECT ar.id, ar.name, ar.zoneid, ar.pollutant, ar.objecttype,
                       ar.reportingmetric, ar.protectiontarget, 
                       ar.assessmentthresholdexceedance,
                       p.notation as pollutant_notation
                FROM assessmentregimes ar
                JOIN eea_pollutants p ON p.uri = ar.pollutant
                WHERE ar.zoneid = %s AND ar.pollutant = %s AND ar.include = true
                ORDER BY ar.objecttype, ar.reportingmetric
            """, (zone_id, pollutant_uri))
        else:
            self.cursor.execute("""
                SELECT ar.id, ar.name, ar.zoneid, ar.pollutant, ar.objecttype,
                       ar.reportingmetric, ar.protectiontarget,
                       ar.assessmentthresholdexceedance,
                       p.notation as pollutant_notation
                FROM assessmentregimes ar
                JOIN eea_pollutants p ON p.uri = ar.pollutant
                WHERE ar.zoneid = %s AND ar.include = true
                ORDER BY p.notation, ar.objecttype, ar.reportingmetric
            """, (zone_id,))
        
        return self.cursor.fetchall()
    
    def get_regime_sampling_points(self, regime_id: str) -> List[str]:
        """
        Get sampling point IDs linked to an assessment regime.
        
        Args:
            regime_id: Assessment regime ID
            
        Returns:
            List of sampling point IDs
        """
        self.cursor.execute("""
            SELECT assessmentlocal_id
            FROM assessmentdata
            WHERE assessmentregime_id = %s
        """, (regime_id,))
        
        return [row['assessmentlocal_id'] for row in self.cursor.fetchall()]
    
    def get_threshold(self, pollutant_notation: str, objecttype: str, 
                     reportingmetric: str, directive: str) -> Optional[Dict[str, Any]]:
        """
        Get threshold value for a specific pollutant/objective/metric/directive.
        
        Args:
            pollutant_notation: Pollutant notation (e.g., 'NO2', 'PM10')
            objecttype: Objective type (e.g., 'LV', 'ALT', 'INT')
            reportingmetric: Reporting metric/statistic (e.g., 'P1Y', 'P1Y-hrsAbove200')
            directive: Directive identifier ('2008/50', '2024/2881', 'WHO')
            
        Returns:
            Threshold dict with 'value' and 'operator', or None if not found
        """
        pollutant_thresholds = DIRECTIVE_THRESHOLDS.get(pollutant_notation)
        if not pollutant_thresholds:
            return None
        
        objective_thresholds = pollutant_thresholds.get(objecttype)
        if not objective_thresholds:
            return None
        
        # Find threshold entry matching reportingmetric
        for threshold_name, threshold_data in objective_thresholds.items():
            if threshold_data.get("statistic") == reportingmetric:
                return threshold_data.get(directive)
        
        return None
    
    def check_threshold(self, value: float, threshold_value: float, operator: str) -> bool:
        """
        Check if a value exceeds a threshold using the specified operator.
        
        Args:
            value: Calculated aggregation value
            threshold_value: Threshold limit
            operator: Comparison operator ('>', '>=', '<', '<=', '==')
            
        Returns:
            True if threshold is exceeded (condition is met)
        """
        if operator == '>':
            return value > threshold_value
        elif operator == '>=':
            return value >= threshold_value
        elif operator == '<':
            return value < threshold_value
        elif operator == '<=':
            return value <= threshold_value
        elif operator == '==':
            return value == threshold_value
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def evaluate_regime(self, regime_id: str, year: int, directive: str) -> Dict[str, Any]:
        """
        Evaluate exceedances for a specific assessment regime.
        
        Args:
            regime_id: Assessment regime ID
            year: Year to evaluate
            directive: Directive identifier ('2008/50', '2024/2881', 'WHO')
            
        Returns:
            Dict with exceedance evaluation results
        """
        # Get regime metadata
        self.cursor.execute("""
            SELECT ar.id, ar.name, ar.zoneid, ar.pollutant, ar.objecttype,
                   ar.reportingmetric, ar.protectiontarget,
                   p.notation as pollutant_notation,
                   z.name as zone_name
            FROM assessmentregimes ar
            JOIN eea_pollutants p ON p.uri = ar.pollutant
            JOIN zones z ON z.id = ar.zoneid
            WHERE ar.id = %s
        """, (regime_id,))
        
        regime = self.cursor.fetchone()
        if not regime:
            raise ValueError(f"Assessment regime not found: {regime_id}")
        
        # Get threshold for this regime/directive
        threshold_data = self.get_threshold(
            regime['pollutant_notation'],
            regime['objecttype'],
            regime['reportingmetric'],
            directive
        )
        
        if not threshold_data:
            return {
                'regime_id': regime_id,
                'regime_name': regime['name'],
                'zone_name': regime['zone_name'],
                'pollutant': regime['pollutant_notation'],
                'objecttype': regime['objecttype'],
                'reportingmetric': regime['reportingmetric'],
                'year': year,
                'directive': directive,
                'threshold_applicable': False,
                'message': f"No threshold defined for {directive}"
            }
        
        # Calculate aggregation using Statistics class
        aggregation_results = self.statistics.generate(
            regime['reportingmetric'],
            regime['pollutant_notation'],
            year
        )
        
        # Get sampling points for this regime
        regime_sampling_points = self.get_regime_sampling_points(regime_id)
        
        # Filter results to only sampling points in this regime
        relevant_results = [
            r for r in aggregation_results 
            if r['spo'] in regime_sampling_points
        ]
        
        if not relevant_results:
            return {
                'regime_id': regime_id,
                'regime_name': regime['name'],
                'zone_name': regime['zone_name'],
                'pollutant': regime['pollutant_notation'],
                'objecttype': regime['objecttype'],
                'reportingmetric': regime['reportingmetric'],
                'year': year,
                'directive': directive,
                'threshold_applicable': True,
                'threshold_value': threshold_data['value'],
                'threshold_operator': threshold_data['operator'],
                'has_data': False,
                'message': "No data available for assessment"
            }
        
        # Find maximum value across all sampling points in regime
        max_result = max(relevant_results, key=lambda x: x['value'])
        max_value = max_result['value']
        
        # Check if threshold is exceeded
        has_exceedance = self.check_threshold(
            max_value,
            threshold_data['value'],
            threshold_data['operator']
        )
        
        # Find all sampling points that exceed threshold
        exceeding_sampling_points = [
            {
                'spo': r['spo'],
                'code': r.get('code', r['spo']),  # Fallback to spo if code not present
                'value': r['value'],
                'coverage': r.get('coverage')
            }
            for r in relevant_results
            if self.check_threshold(r['value'], threshold_data['value'], threshold_data['operator'])
        ]
        
        return {
            'regime_id': regime_id,
            'regime_name': regime['name'],
            'zone_name': regime['zone_name'],
            'pollutant': regime['pollutant_notation'],
            'objecttype': regime['objecttype'],
            'reportingmetric': regime['reportingmetric'],
            'year': year,
            'directive': directive,
            'threshold_applicable': True,
            'threshold_value': threshold_data['value'],
            'threshold_operator': threshold_data['operator'],
            'has_data': True,
            'has_exceedance': has_exceedance,
            'max_value': max_value,
            'max_value_coverage': max_result.get('coverage'),
            'sampling_points_count': len(relevant_results),
            'exceeding_sampling_points_count': len(exceeding_sampling_points),
            'exceeding_sampling_points': exceeding_sampling_points
        }
    
    def evaluate_zone(self, zone_id: str, year: int, directive: str, 
                     pollutant_notation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Evaluate all exceedances for a zone.
        
        Args:
            zone_id: Zone identifier
            year: Year to evaluate
            directive: Directive identifier ('2008/50', '2024/2881', 'WHO')
            pollutant_notation: Optional pollutant filter (e.g., 'NO2')
            
        Returns:
            List of exceedance evaluation results for each regime
        """
        regimes = self.get_assessment_regimes(zone_id, pollutant_notation)
        
        results = []
        for regime in regimes:
            try:
                result = self.evaluate_regime(regime['id'], year, directive)
                results.append(result)
            except Exception as e:
                results.append({
                    'regime_id': regime['id'],
                    'regime_name': regime['name'],
                    'error': str(e)
                })
        
        return results
