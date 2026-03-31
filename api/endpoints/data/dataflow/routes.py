from flask import jsonify, Blueprint, request, Response
from werkzeug.exceptions import BadRequest
from core.utils import U
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_exporting_claim
from core.data import dataflow as DataflowExports
import zipfile
from io import BytesIO
from datetime import datetime

dataflow_endpoint = Blueprint('dataflow', __name__)


# NEW CSV EXPORTS (Reportnet3 format)

@dataflow_endpoint.route("/api/dataflow/csv/available_years", methods=['GET'])
@jwt_required_with_exporting_claim()
def get_available_years():
    """Get available years from sampling_points from_time and to_time"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT DISTINCT EXTRACT(YEAR FROM year_date)::integer as year
            FROM (
                SELECT from_time as year_date FROM sampling_points WHERE from_time IS NOT NULL
                UNION
                SELECT to_time as year_date FROM sampling_points WHERE to_time IS NOT NULL
            ) years
            ORDER BY year DESC
        """)
        years = cursor.fetchall()
        return jsonify([row['year'] for row in years])


@dataflow_endpoint.route("/api/dataflow/csv/authorities", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_authorities_csv():
    """Export authorities as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
    
    csv_content = DataflowExports.get_authorities_csv(country_code)
    return U.csv_response(csv_content, "Authority.csv")


@dataflow_endpoint.route("/api/dataflow/csv/stations", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_stations_csv():
    """Export stations as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        timezone_id = settings_row['timezone_id'] if settings_row else None
    
    csv_content = DataflowExports.get_stations_csv(country_code, timezone_id)
    return U.csv_response(csv_content, "Station.csv")


@dataflow_endpoint.route("/api/dataflow/csv/samplingpoints", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_samplingpoints_csv():
    """Export sampling points as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
    
    csv_content = DataflowExports.get_samplingpoints_csv(country_code)
    return U.csv_response(csv_content, "SamplingPoint.csv")


@dataflow_endpoint.route("/api/dataflow/csv/processes", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_processes_csv():
    """Export processes as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
    
    csv_content = DataflowExports.get_processes_csv(country_code)
    return U.csv_response(csv_content, "SamplingPointProcess.csv")


@dataflow_endpoint.route("/api/dataflow/csv/measurements", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_measurements_csv():
    """Export measurement results as CSV matching Reportnet3 format for a specific year"""
    data = request.get_json() or {}
    year = data.get('year')
    
    if not year:
        raise BadRequest("Year parameter is required")
    
    try:
        year = int(year)
    except ValueError:
        raise BadRequest("Year must be a valid integer")
    
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        timezone_id = settings_row['timezone_id'] if settings_row else None
    
    csv_content = DataflowExports.get_measurements_csv(country_code, timezone_id, year)
    return U.csv_response(csv_content, f"MeasurementResult_{year}.csv")


@dataflow_endpoint.route("/api/dataflow/csv/zonegeometry", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_zonegeometry_csv():
    """Export zone geometry as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
    
    csv_content = DataflowExports.get_zonegeometry_csv(country_code)
    return U.csv_response(csv_content, "ZoneGeometry.csv")


@dataflow_endpoint.route("/api/dataflow/csv/spatialrepresentativeness", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_spatial_representativeness():
    """Export SpatialRepresentativeness as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None

    csv_content = DataflowExports.get_spatial_representativeness_csv(country_code)
    return U.csv_response(csv_content, "SpatialRepresentativeness.csv")


@dataflow_endpoint.route("/api/dataflow/csv/srareainline", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_sr_area_inline():
    """Export SRAreaInline as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None

    csv_content = DataflowExports.get_sr_area_inline_csv(country_code)
    return U.csv_response(csv_content, "SRAreaInline.csv")


@dataflow_endpoint.route("/api/dataflow/csv/download_all", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_all_csv():
    """Export all dataflow CSVs as a ZIP file (optionally includes measurements for a specific year)"""
    data = request.get_json() or {}
    year = data.get('year')
    
    # Get settings once for all exports
    with CursorFromPool() as cursor:
        cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        timezone_id = settings_row['timezone_id'] if settings_row else None
    
    # Create a BytesIO buffer for the ZIP file
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add Authority CSV
        csv_content = DataflowExports.get_authorities_csv(country_code)
        if csv_content:
            zip_file.writestr('Authority.csv', csv_content)
        
        # Add Station CSV
        csv_content = DataflowExports.get_stations_csv(country_code, timezone_id)
        if csv_content:
            zip_file.writestr('Station.csv', csv_content)
        
        # Add SamplingPoint CSV
        csv_content = DataflowExports.get_samplingpoints_csv(country_code)
        if csv_content:
            zip_file.writestr('SamplingPoint.csv', csv_content)
        
        # Add SamplingPointProcess CSV
        csv_content = DataflowExports.get_processes_csv(country_code)
        if csv_content:
            zip_file.writestr('SamplingPointProcess.csv', csv_content)
        
        # Add MeasurementResult CSV (if year provided)
        if year:
            try:
                year_int = int(year)
                csv_content = DataflowExports.get_measurements_csv(country_code, timezone_id, year_int)
                if csv_content:
                    zip_file.writestr(f'MeasurementResult_{year_int}.csv', csv_content)
            except (ValueError, TypeError):
                pass  # Skip measurements if year is invalid
        
        # Add ZoneGeometry CSV
        csv_content = DataflowExports.get_zonegeometry_csv(country_code)
        if csv_content:
            zip_file.writestr('ZoneGeometry.csv', csv_content)

        # Add SpatialRepresentativeness CSV
        csv_content = DataflowExports.get_spatial_representativeness_csv(country_code)
        if csv_content:
            zip_file.writestr('SpatialRepresentativeness.csv', csv_content)

        # Add SRAreaInline CSV
        csv_content = DataflowExports.get_sr_area_inline_csv(country_code)
        if csv_content:
            zip_file.writestr('SRAreaInline.csv', csv_content)
    
    # Prepare the ZIP file for download
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    response = Response(zip_buffer.read(), mimetype='application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename=dataflow_export_{timestamp}.zip'
    zip_buffer.close()
    
    return response


