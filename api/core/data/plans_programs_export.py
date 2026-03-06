"""
Plans & Programs exceedances export logic.

This module transforms RAVEN exceedances data into EEA-compliant format
for integration with the Plans & Programs (Flow H-K) module.

The export:
1. Evaluates exceedances using existing RAVEN logic
2. Generates EEA-compliant IDs
3. Maps pollutants to EEA codes
4. Maps assessment types to EEA format
5. Includes context data for UI display
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from core.eea.id_generator import EEAIDGenerator, get_or_validate_country_code
from core.data.exceedances import (
    Exceedances,
    DIRECTIVE_THRESHOLDS,
    get_pollutant_eea_code,
    map_assessment_type
)
from core.data.statistics import Statistics


class PlansAndProgramsExport:
    """Export exceedances in Plans & Programs EEA-compliant format."""
    
    def __init__(self, cursor):
        """
        Initialize exporter.
        
        Args:
            cursor: Database cursor (psycopg2)
        """
        self.cursor = cursor
        self.exceedances = Exceedances(cursor)
        self.statistics = Statistics(cursor)
        self.id_generator = EEAIDGenerator()
    
    def export_exceedances(
        self,
        countrycode: Optional[str],
        reportingyear: int,
        directive: str = "2024/2881",
        pollutants: List[str] = None,
        zones: List[str] = None,
        exceedances_only: bool = True,
        assessment_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Export exceedances formatted for Plans & Programs.
        
        Args:
            countrycode: ISO 2-letter country code (or None to use settings)
            reportingyear: Year to evaluate
            directive: EU directive ('2008/50', '2024/2881', 'WHO')
            pollutants: Filter by pollutant notations (empty = all)
            zones: Filter by zone IDs (empty = all)
            exceedances_only: Only return exceeded thresholds
            assessment_types: Filter by assessment type (empty = all)
        
        Returns:
            Dictionary with metadata and formatted exceedances array
        """
        # Get and validate country code
        validated_country_code = get_or_validate_country_code(
            self.cursor,
            countrycode
        )
        
        # Query exceedances with full context
        exceedances_data = self._query_exceedances(
            countrycode=validated_country_code,
            reportingyear=reportingyear,
            directive=directive,
            pollutants=pollutants or [],
            zones=zones or [],
            exceedances_only=exceedances_only,
            assessment_types=assessment_types or []
        )
        
        # Transform to EEA format
        formatted_exceedances = []
        compliance_sequence = 1
        
        for row in exceedances_data:
            formatted = self._format_exceedance(
                row,
                validated_country_code,
                reportingyear,
                directive,
                compliance_sequence
            )
            if formatted:  # Only add if formatting succeeded
                formatted_exceedances.append(formatted)
                compliance_sequence += 1
        
        # Generate metadata
        metadata = self._generate_metadata(
            validated_country_code,
            reportingyear,
            directive,
            formatted_exceedances
        )
        
        # Generate zone summaries
        zone_summaries = self._generate_zone_summaries(formatted_exceedances)
        
        return {
            "success": True,
            "metadata": metadata,
            "exceedances": formatted_exceedances,
            "zone_summaries": zone_summaries
        }
    
    def _query_exceedances(
        self,
        countrycode: str,
        reportingyear: int,
        directive: str,
        pollutants: List[str],
        zones: List[str],
        exceedances_only: bool,
        assessment_types: List[str]
    ) -> List[Dict]:
        """
        Query database for exceedances with full context.
        
        Uses spatial join for zones and includes all metadata needed
        for EEA format transformation.
        """
        # Build WHERE clauses
        where_clauses = []
        params = {
            'reportingyear': reportingyear,
            'reportingyear_start': f'{reportingyear}-01-01 00:00:00',
            'reportingyear_end': f'{reportingyear}-12-31 23:59:59'
        }
        
        # Filter by pollutants if specified
        if pollutants:
            where_clauses.append("p.notation = ANY(%(pollutants)s)")
            params['pollutants'] = pollutants
        
        # Filter by zones if specified
        if zones:
            where_clauses.append("z.id = ANY(%(zones)s)")
            params['zones'] = zones
        
        # Filter by assessment types if specified
        if assessment_types:
            # Map back to RAVEN notations
            raven_notations = [
                k for k, v in map_assessment_type.__globals__.get('ASSESSMENT_TYPE_MAPPING', {}).items()
                if v in assessment_types
            ]
            if raven_notations:
                where_clauses.append("eat.notation = ANY(%(assessment_types)s)")
                params['assessment_types'] = raven_notations
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Main query with spatial join for zones
        # v4 schema: assessment_type is on assessmentdata, zones have no year
        # v4 schema: stations have latitude/longitude columns directly (not PostGIS geom)
        # v4 schema: processes table doesn't have uncertainty_estimate/detection_limit
        query = f"""
        SELECT 
            -- Sampling point & station
            sp.id as sampling_point_id,
            sp.id as sampling_point_code,
            st.name as station_name,
            st.eoi_code as station_code,
            st.longitude as longitude,
            st.latitude as latitude,
            
            -- Zone (via assessment_regimes) - v4 schema
            z.id as zone_id,
            z.code as zone_code,
            z.name as zone_name,
            zc.notation as zone_category,
            
            -- Pollutant
            p.notation as pollutant,
            p.label as pollutant_label,
            p.uri as pollutant_uri,
            
            -- Network
            n.name as network_name,
            n.id as network_id,
            
            -- Assessment type (from assessmentdata in v4 schema)
            eat.notation as assessment_type_notation,
            eat.label as assessment_type_label
            
        FROM sampling_points sp
        JOIN stations st ON sp.station_id = st.id
        JOIN eea_pollutants p ON sp.pollutant_id = p.id
        JOIN networks n ON st.network_id = n.id
        -- v4: assessment_type is on assessmentdata, not sampling_points
        LEFT JOIN assessmentdata ad ON ad.assessmentlocal_id = sp.id
        LEFT JOIN eea_assessmenttypes eat ON ad.assessmenttype = eat.id
        -- v4: zones have no year column, join via assessment_regimes
        LEFT JOIN assessment_regimes ar ON ad.assessment_regime_id = ar.id
        LEFT JOIN zones z ON ar.zone_id = z.id
        LEFT JOIN eea_zonecategory zc ON z.zone_category_id = zc.id
        
        WHERE 1=1
          AND sp.from_time <= %(reportingyear_end)s::timestamp
          AND (sp.to_time IS NULL OR sp.to_time >= %(reportingyear_start)s::timestamp)
          AND {where_sql}
        
        ORDER BY z.code, p.notation
        """
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def _format_exceedance(
        self,
        row: Dict,
        countrycode: str,
        reportingyear: int,
        directive: str,
        sequence: int
    ) -> Optional[Dict]:
        """
        Format a single exceedance row to EEA structure.
        
        Returns None if formatting fails (e.g., no threshold data).
        """
        try:
            pollutant = row['pollutant']
            zone_code = row.get('zone_code') or row.get('zone_id') or 'UNKNOWN'
            zone_name = row.get('zone_name') or zone_code
            
            # Generate EEA IDs
            assessment_regime_id = self.id_generator.generate_assessment_regime_id(
                countrycode, zone_name, pollutant, reportingyear
            )
            compliance_id = self.id_generator.generate_compliance_id(
                countrycode, reportingyear, sequence
            )
            assessment_method_id = self.id_generator.generate_assessment_method_id(
                countrycode, zone_name, pollutant, sequence
            )
            attainment_id = self.id_generator.generate_attainment_id(
                countrycode, reportingyear, zone_name, pollutant
            )
            sr_id = self.id_generator.generate_sr_id(row['sampling_point_id'])
            
            # Get EEA pollutant code
            air_pollutant_code = get_pollutant_eea_code(pollutant)
            
            # Map assessment type
            assessment_type = map_assessment_type(row.get('assessment_type_notation', ''))
            
            # For now, create a placeholder structure
            # TODO: Integrate with actual exceedance evaluation
            # This will be enhanced to pull real aggregated values
            
            return {
                # EEA Compliance Structure
                "countrycode": countrycode,
                "assessmentregimeid": assessment_regime_id,
                "dataaggregationprocessid": "P1Y",  # TODO: Get from actual statistic
                "assessmentmethodid": assessment_method_id,
                "complianceid": compliance_id,
                "reportingyear": reportingyear,
                "airpollutantcode": air_pollutant_code,
                "assessmenttype": assessment_type,
                "hotspot": False,
                "isexceedance": "unknown",  # TODO: Calculate from threshold evaluation
                "airpollutionlevel": None,  # TODO: Get from aggregation
                "airpollutionleveladjusted": None,
                "absoluteuncertaintylimit": row.get('uncertainty_estimate'),
                "relativeuncertaintylimit": None,
                "maxratiouncertainty": None,
                "correctionfactor": False,
                "attainmentid": attainment_id,
                "sr_id": sr_id,
                "preliminaryreason": None,
                
                # Nested context for UI display (expected by raven-plan-program import)
                "zone": {
                    "id": row.get('zone_id'),
                    "code": zone_code,
                    "name": zone_name,
                    "category": row.get('zone_category'),
                    "inspireId": f"{countrycode}.AQ.ZONE.{zone_code}" if zone_code else None
                },
                "station": {
                    "name": row['station_name'],
                    "code": row['station_code'],
                    "eoi_code": row['station_code'],
                    "inspireId": f"{countrycode}.AQ.STATION.{row['station_code']}" if row.get('station_code') else None,
                    "longitude": float(row['longitude']) if row.get('longitude') else None,
                    "latitude": float(row['latitude']) if row.get('latitude') else None
                },
                "pollutant": {
                    "notation": pollutant,
                    "label": row['pollutant_label'],
                    "eea_code": air_pollutant_code
                },
                "threshold": {
                    "objective": None,  # TODO: Get from threshold data
                    "objectivetype": None,
                    "value": None,
                    "unit": "µg/m³",
                    "operator": ">",
                    "directive": directive
                },
                "measurement": {
                    "value": None,  # TODO: Get from aggregation
                    "coverage": None,
                    "exceeded_by": None,
                    "exceeded_by_percent": None
                },
                "network": {
                    "name": row['network_name'],
                    "id": row['network_id']
                }
            }
        
        except Exception as e:
            # Log error but continue processing other rows
            print(f"Error formatting exceedance for sampling point {row.get('sampling_point_id')}: {e}")
            return None
    
    def _generate_metadata(
        self,
        countrycode: str,
        reportingyear: int,
        directive: str,
        exceedances: List[Dict]
    ) -> Dict:
        """Generate response metadata."""
        pollutants_exceeded = list(set([
            exc['pollutant']['notation']
            for exc in exceedances
            if exc.get('isexceedance') == 'yes'
        ]))
        
        zones_affected = len(set([
            exc['zone']['code']
            for exc in exceedances
            if exc.get('isexceedance') == 'yes' and exc.get('zone', {}).get('code')
        ]))
        
        return {
            "countrycode": countrycode,
            "reportingyear": reportingyear,
            "directive": directive,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_exceedances": len([e for e in exceedances if e.get('isexceedance') == 'yes']),
            "total_evaluated": len(exceedances),
            "zones_affected": zones_affected,
            "pollutants_exceeded": sorted(pollutants_exceeded)
        }
    
    def _generate_zone_summaries(self, exceedances: List[Dict]) -> List[Dict]:
        """Generate zone-level summaries."""
        zones = {}
        
        for exc in exceedances:
            if exc.get('isexceedance') != 'yes':
                continue
            
            zone_code = exc.get('zone', {}).get('code')
            if not zone_code or zone_code == 'UNKNOWN':
                continue
            
            if zone_code not in zones:
                zones[zone_code] = {
                    "zoneid": exc.get('zone', {}).get('id'),
                    "zonename": exc.get('zone', {}).get('name'),
                    "exceedances_count": 0,
                    "pollutants": set(),
                    "worst_exceedance": None
                }
            
            zone = zones[zone_code]
            zone['exceedances_count'] += 1
            zone['pollutants'].add(exc.get('pollutant', {}).get('notation'))
            
            # Track worst exceedance
            exceeded_by_pct = exc.get('measurement', {}).get('exceeded_by_percent')
            if exceeded_by_pct and (zone['worst_exceedance'] is None or 
                                    exceeded_by_pct > zone['worst_exceedance'].get('exceeded_by_percent', 0)):
                zone['worst_exceedance'] = {
                    "pollutant": exc.get('pollutant', {}).get('notation'),
                    "value": exc.get('airpollutionlevel'),
                    "threshold": exc.get('threshold', {}).get('value'),
                    "exceeded_by_percent": exceeded_by_pct
                }
        
        # Convert sets to sorted lists
        for zone in zones.values():
            zone['pollutants'] = sorted(list(zone['pollutants']))
        
        return list(zones.values())
