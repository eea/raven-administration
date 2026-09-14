"""
API routes for Plans & Programs exceedances export.

Provides endpoint: POST /api/exports/exceedances/plans-and-programs
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from core.database import CursorFromPool
from core.jwt_ext_custom import api_key_or_jwt_required
from core.data.plans_programs_export import PlansAndProgramsExport
from .models import PlansAndProgramsExportRequest


plans_programs_endpoint = Blueprint('export_plans_programs', __name__)


@plans_programs_endpoint.route('/api/exports/exceedances/plans-and-programs', methods=['POST'])
@api_key_or_jwt_required('management', 'allnetworks')
def export_exceedances_plans_programs():
    """
    Export exceedances formatted for EEA Plans & Programs (Flow H-K) wizard.
    
    This endpoint evaluates air quality exceedances against directive thresholds
    and formats the results in EEA-compliant structure for integration with the
    Plans & Programs module.
    
    Request Body:
        {
            "countrycode": "AD",          // Optional - uses settings.country_code_id if not provided
            "reportingyear": 2024,        // Required - year to evaluate
            "directive": "2024/2881",     // Optional - default: "2024/2881"
            "pollutants": ["NO2", "PM10"], // Optional - empty = all pollutants
            "zones": [],                  // Optional - empty = all zones
            "exceedances_only": true      // Optional - default: true
        }
    
    Response:
        {
            "success": true,
            "metadata": {
                "countrycode": "AD",
                "reportingyear": 2024,
                "directive": "2024/2881",
                "generated_at": "2024-01-30T12:00:00Z",
                "total_exceedances": 15,
                "zones_affected": 3,
                "pollutants_exceeded": ["NO2", "PM10"]
            },
            "exceedances": [
                {
                    "countrycode": "AD",
                    "assessmentregimeid": "ARE_ZON_AD000A_0008_LV_H_aMean_2021_1",
                    "dataaggregationprocessid": "P1Y",
                    "assessmentmethodid": "SPO-AD0940A-0008",
                    "reportingyear": 2024,
                    "pollutantid": 8,
                    # The regime id with the classification year swapped for the
                    # reporting year: one attainment per regime per year, shared by every
                    # assessment method assessing it. The trailing index is the stored
                    # AttainmentIndex, and over HTTP there is no stored row to read, so
                    # this is always the index-1 form. `attainmentbase` is the same
                    # identifier without it.
                    "attainmentid": "ATT_ZON_AD000A_0008_LV_H_aMean_2024_1",
                    "attainmentbase": "ATT_ZON_AD000A_0008_LV_H_aMean_2024",
                    # CAM_16 is entered on the Compliance Assessment Method screen, not
                    # derived, so it is null here.
                    "srsid": None,
                    "assessmenttype": "fixed",
                    "isexceedance": "yes",
                    "airpollutionlevel": 45.2,
                    ...
                    # The context blocks are flat siblings, not nested under a wrapper.
                    "zone": {...},
                    "station": {...},
                    "pollutant": {...},
                    "threshold": {...},
                    "measurement": {...}
                }
            ],
            # Sampling points the derivation deliberately did not produce a row for --
            # today, one whose pollutant contradicts the regime it is linked to. Each
            # carries a `code` and a `reason`.
            "skipped": [...],
            # How many sampling points were left out as not part of the EEA reporting
            # obligation (report_to_eea, migration 022).
            "out_of_scope": 0,
            "zone_summaries": [...]
        }
    
    Authentication:
        Requires JWT token with 'management' and 'allnetworks' claims
    
    Errors:
        400 - Validation error (invalid parameters)
        401 - Unauthorized (missing or invalid token)
        403 - Forbidden (insufficient permissions)
        500 - Internal server error
    
    Example:
        curl -X POST http://localhost:5000/api/exports/exceedances/plans-and-programs \\
             -H "Authorization: Bearer <token>" \\
             -H "Content-Type: application/json" \\
             -d '{"reportingyear": 2024, "pollutants": ["NO2"]}'
    """
    try:
        # Validate request using Pydantic model
        model = PlansAndProgramsExportRequest(**request.json)
    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters",
                "details": e.errors()
            }
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "REQUEST_ERROR",
                "message": str(e)
            }
        }), 400
    
    try:
        with CursorFromPool() as cursor:
            exporter = PlansAndProgramsExport(cursor)
            
            result = exporter.export_exceedances(
                countrycode=model.countrycode,
                reportingyear=model.reportingyear,
                directive=model.directive,
                pollutants=model.pollutants,
                zones=model.zones,
                exceedances_only=model.exceedances_only,
                assessment_types=model.assessment_types
            )
        
        return jsonify(result), 200
    
    except ValueError as e:
        # Country code validation or other value errors
        return jsonify({
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        }), 400
    
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error in Plans & Programs export: {e}")
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An error occurred while exporting exceedances",
                "details": str(e) if request.args.get('debug') else None
            }
        }), 500


@plans_programs_endpoint.route('/api/exports/exceedances/plans-and-programs/info', methods=['GET'])
@api_key_or_jwt_required('management', 'allnetworks')
def get_export_info():
    """
    Get information about the Plans & Programs export endpoint.
    
    Returns available directives, pollutants, and other metadata.
    
    Response:
        {
            "success": true,
            "endpoint": "/api/exports/exceedances/plans-and-programs",
            "method": "POST",
            "supported_directives": ["2008/50", "2024/2881", "WHO"],
            "supported_pollutants": ["NO2", "PM10", "PM2.5", "SO2", "O3", "CO", ...],
            "authentication": {
                "required": true,
                "claims": ["management", "allnetworks"]
            },
            "documentation": "https://docs.raven-aq.eu/api/exports/plans-and-programs"
        }
    """
    from core.data.exceedances import POLLUTANT_EEA_CODES
    
    return jsonify({
        "success": True,
        "endpoint": "/api/exports/exceedances/plans-and-programs",
        "method": "POST",
        "description": "Export exceedances formatted for EEA Plans & Programs (Flow H-K)",
        "supported_directives": ["2008/50", "2024/2881", "WHO"],
        "supported_pollutants": sorted(list(POLLUTANT_EEA_CODES.keys())),
        "supported_assessment_types": ["fixed", "indicative", "modelling"],
        "authentication": {
            "required": True,
            "claims": ["management", "allnetworks"],
            "description": "Requires JWT token with management and allnetworks claims"
        },
        "parameters": {
            "countrycode": {
                "type": "string",
                "required": False,
                "description": "ISO 2-letter country code (defaults to settings.country_code_id)"
            },
            "reportingyear": {
                "type": "integer",
                "required": True,
                "description": "Year to evaluate exceedances"
            },
            "directive": {
                "type": "string",
                "required": False,
                "default": "2024/2881",
                "description": "EU Air Quality Directive"
            },
            "pollutants": {
                "type": "array",
                "required": False,
                "default": [],
                "description": "Filter by pollutant notations (empty = all)"
            },
            "zones": {
                "type": "array",
                "required": False,
                "default": [],
                "description": "Filter by zone IDs (empty = all)"
            },
            "exceedances_only": {
                "type": "boolean",
                "required": False,
                "default": True,
                "description": "Only return actual exceedances"
            }
        }
    }), 200
