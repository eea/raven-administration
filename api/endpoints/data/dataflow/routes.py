from flask import jsonify, Blueprint, request, current_app, Response
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.query import Q
from core.utils import U
from core.database import CursorFromPool
from endpoints.data.dataflow.models import DataflowModel, DataflowModelE2a
from core.eea.dataflows import Dataflows
from core.eea.dataflows_reportnet3 import Dataflows_reportnet3
from core.jwt_ext_custom import jwt_required_with_exporting_claim
import zipfile
from io import BytesIO, StringIO
import pandas as pd
import csv
import json
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
        # Get country code from settings
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                a.id as authority_instance_id,
                COALESCE(ao.notation, '') as object,
                a.email,
                COALESCE(ai.notation, '') as authority_instance,
                a.organisation_name,
                COALESCE(a.organisation_url, '') as organisation_url,
                COALESCE(a.organisation_address, '') as organisation_address,
                COALESCE(a.person_name, '') as person_name,
                COALESCE(ast.notation, '') as authority_status
            FROM authorities a
            LEFT JOIN eea_authorityinstance ai ON a.instance_id = ai.id
            LEFT JOIN eea_authorityobject ao ON a.object_id = ao.id
            LEFT JOIN eea_authoritystatus ast ON a.status_id = ast.id
            ORDER BY a.id
        """, (country_code,))
        authorities = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if authorities:
            fieldnames = [
                'Country Code', 'Authority Instance Id', 'Object', 'Email',
                'Authority Instance', 'Organisation Name', 'Organisation URL',
                'Organisation Address', 'Person Name', 'Authority Status'
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in authorities:
                writer.writerow({
                    'Country Code': row['country_code'],
                    'Authority Instance Id': row['authority_instance_id'],
                    'Object': row['object'],
                    'Email': row['email'],
                    'Authority Instance': row['authority_instance'],
                    'Organisation Name': row['organisation_name'],
                    'Organisation URL': row['organisation_url'],
                    'Organisation Address': row['organisation_address'],
                    'Person Name': row['person_name'],
                    'Authority Status': row['authority_status']
                })
        
        return U.csv_response(csv_buffer.getvalue(), "Authority.csv")


@dataflow_endpoint.route("/api/dataflow/csv/stations", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_stations_csv():
    """Export stations as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        # Get country code and timezone from settings
        cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        timezone_id = settings_row['timezone_id'] if settings_row else None
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                s.eoi_code as air_quality_station_eoi_code,
                s.network_id as air_quality_network,
                n.name as air_quality_network_name,
                al.notation as air_quality_network_organisational_level,
                %s as timezone,
                s.national_code as air_quality_station_nat_code,
                s.name as aq_station_name,
                n.report_id as network_report_id
            FROM stations s
            JOIN networks n ON s.network_id = n.id
            LEFT JOIN eea_administrativelevels al ON n.administration_level_id = al.id
            ORDER BY s.id
        """, (country_code, timezone_id))
        stations = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if stations:
            fieldnames = [
                'CountryCode', 'AirQualityStationEoICode', 'Air Quality Network',
                'Air Quality Network Name', 'Air Quality Network Organisational Level',
                'Timezone', 'Air Quality Station Nat Code', 'AQ Station Name', 
                'NetworkReportId'
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in stations:
                writer.writerow({
                    'CountryCode': row['country_code'],
                    'AirQualityStationEoICode': row['air_quality_station_eoi_code'],
                    'Air Quality Network': row['air_quality_network'],
                    'Air Quality Network Name': row['air_quality_network_name'],
                    'Air Quality Network Organisational Level': row['air_quality_network_organisational_level'],
                    'Timezone': row['timezone'],
                    'Air Quality Station Nat Code': row['air_quality_station_nat_code'] or '',
                    'AQ Station Name': row['aq_station_name'],
                    'NetworkReportId': row['network_report_id'] or ''
                })
        
        return U.csv_response(csv_buffer.getvalue(), "Station.csv")


@dataflow_endpoint.route("/api/dataflow/csv/samplingpoints", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_samplingpoints_csv():
    """Export sampling points as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        # Get country code from settings
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                sp.id as assessment_method_id,
                sp.sampling_point_ref,
                po.notation as air_pollutant_code,
                st.eoi_code as air_quality_station_eoi_code,
                ac.notation as air_quality_station_area,
                sc.notation as air_quality_spo_category,
                st.supersite as super_site,
                st.latitude,
                st.longitude,
                st.altitude as altitude_masl,
                sp.inlet_height as inlet_height_m,
                sp.building_distance as building_distance_m,
                sp.kerb_distance as kerb_distance_m,
                sp.emission_source_distance as emission_source_distance_m
            FROM sampling_points sp
            JOIN stations st ON sp.station_id = st.id
            JOIN eea_pollutants po ON sp.pollutant_id = po.id
            LEFT JOIN eea_areaclassifications ac ON st.area_classification_id = ac.id
            LEFT JOIN eea_spocategory sc ON sp.spo_category_id = sc.id
            ORDER BY sp.id
        """, (country_code,))
        samplingpoints = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if samplingpoints:
            fieldnames = [
                'CountryCode', 'Assessment Method Id', 'Sampling Point Ref',
                'AirPollutantCode', 'Air Quality Station Eo I Code', 
                'Air Quality Station Area', 'AirQualitySPOCategory', 'Super Site',
                'Latitude', 'Longitude', 'Altitude(masl)', 'InletHeight(m)',
                'BuildingDistance(m)', 'KerbDistance(m)', 'EmissionSourceDistance(m)'
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in samplingpoints:
                writer.writerow({
                    'CountryCode': row['country_code'],
                    'Assessment Method Id': row['assessment_method_id'],
                    'Sampling Point Ref': row['sampling_point_ref'] or '',
                    'AirPollutantCode': row['air_pollutant_code'],
                    'Air Quality Station Eo I Code': row['air_quality_station_eoi_code'],
                    'Air Quality Station Area': row['air_quality_station_area'] or '',
                    'AirQualitySPOCategory': row['air_quality_spo_category'] or '',
                    'Super Site': 'true' if row['super_site'] else 'false',
                    'Latitude': row['latitude'],
                    'Longitude': row['longitude'],
                    'Altitude(masl)': row['altitude_masl'] or '',
                    'InletHeight(m)': row['inlet_height_m'] or '',
                    'BuildingDistance(m)': row['building_distance_m'] or '',
                    'KerbDistance(m)': row['kerb_distance_m'] or '',
                    'EmissionSourceDistance(m)': row['emission_source_distance_m'] or ''
                })
        
        return U.csv_response(csv_buffer.getvalue(), "SamplingPoint.csv")


@dataflow_endpoint.route("/api/dataflow/csv/processes", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_processes_csv():
    """Export processes as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        # Get country code from settings
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                p.id as process_id,
                sp.id as assessment_method_id,
                p.activity_begin as process_activity_begin,
                p.activity_end as process_activity_end,
                po.notation as air_pollutant_code,
                mt.notation as measurement_type,
                mm.notation as method,
                me.notation as equipment,
                at.notation as analytical_technique,
                ed.notation as equivalence_demonstrated,
                p.data_quality_report_id,
                p.equivalence_demonstration_report_id,
                p.process_documentation_id
            FROM processes p
            JOIN sampling_points sp ON p.sampling_point_id = sp.id
            JOIN eea_pollutants po ON sp.pollutant_id = po.id
            LEFT JOIN eea_measurementtypes mt ON p.measurement_type_id = mt.id
            LEFT JOIN eea_measurementmethods mm ON p.method_id = mm.id
            LEFT JOIN eea_measurementequipments me ON p.equipment_id = me.id
            LEFT JOIN eea_analyticaltechnique at ON p.analytical_technique_id = at.id
            LEFT JOIN eea_equivalencedemonstrated ed ON p.equivalence_demonstrated_id = ed.id
            ORDER BY p.id
        """, (country_code,))
        processes = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if processes:
            fieldnames = [
                'CountryCode', 'Process Id', 'AssessmentMethodId',
                'Process Activity Begin', 'Process Activity End', 'AirPollutantCode',
                'Measurement Type', 'Method', 'Equipment', 'Analytical Technique',
                'Equivalence Demonstrated', 'Data Quality Report Id',
                'Equivalence Demonstration Report Id', 'Process Documentation Id'
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in processes:
                writer.writerow({
                    'CountryCode': row['country_code'],
                    'Process Id': row['process_id'],
                    'AssessmentMethodId': row['assessment_method_id'],
                    'Process Activity Begin': row['process_activity_begin'],
                    'Process Activity End': row['process_activity_end'] or '',
                    'AirPollutantCode': row['air_pollutant_code'],
                    'Measurement Type': row['measurement_type'] or '',
                    'Method': row['method'] or '',
                    'Equipment': row['equipment'] or '',
                    'Analytical Technique': row['analytical_technique'] or '',
                    'Equivalence Demonstrated': row['equivalence_demonstrated'] or '',
                    'Data Quality Report Id': row['data_quality_report_id'] or '',
                    'Equivalence Demonstration Report Id': row['equivalence_demonstration_report_id'] or '',
                    'Process Documentation Id': row['process_documentation_id'] or ''
                })
        
        return U.csv_response(csv_buffer.getvalue(), "SamplingPointProcess.csv")


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
        # Get country code and timezone from settings
        cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        timezone_id = settings_row['timezone_id'] if settings_row else None
        
        # Get timezone offset for appending to timestamps (ISO 8601 format)
        timezone_offset = ''
        if timezone_id:
            cursor.execute("SELECT timezone_offset FROM eea_timezones WHERE id = %s", (timezone_id,))
            tz_row = cursor.fetchone()
            timezone_offset = tz_row['timezone_offset'] if tz_row else ''
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                sp.id as assessment_method_id,
                o.from_time,
                po.notation as air_pollutant_code,
                o.to_time,
                o.value,
                co.notation as unit,
                ov.notation as validity,
                ove.notation as verification,
                NULL as data_capture,
                tr.notation as time_resolution,
                o.touched as result_time
            FROM observations o
            JOIN sampling_points sp ON o.sampling_point_id = sp.id
            JOIN eea_pollutants po ON sp.pollutant_id = po.id
            JOIN eea_concentrations co ON sp.unit_id = co.id
            JOIN eea_times tr ON sp.time_resolution_id = tr.id
            LEFT JOIN eea_observationvalidity ov ON o.observationvalidity_id = ov.id
            LEFT JOIN eea_observationverification ove ON o.observationverification_id = ove.id
            WHERE EXTRACT(YEAR FROM o.from_time) = %s
            ORDER BY sp.id, o.from_time
        """, (country_code, year))
        measurements = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if measurements:
            fieldnames = [
                'CountryCode', 'AssessmentMethodId', 'Start', 'AirPollutantCode',
                'End', 'Value', 'Unit', 'Validity', 'Verification',
                'Data Capture', 'Time Resolution', 'Result Time'
            ]
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in measurements:
                # Format timestamps with timezone offset (ISO 8601 format)
                start_time = row['from_time'].strftime('%Y-%m-%d %H:%M:%S')
                end_time = row['to_time'].strftime('%Y-%m-%d %H:%M:%S')
                result_time = row['result_time'].strftime('%Y-%m-%d %H:%M:%S')
                
                if timezone_offset:
                    start_time = f"{start_time}{timezone_offset}"
                    end_time = f"{end_time}{timezone_offset}"
                    result_time = f"{result_time}{timezone_offset}"
                
                writer.writerow({
                    'CountryCode': row['country_code'],
                    'AssessmentMethodId': row['assessment_method_id'],
                    'Start': start_time,
                    'AirPollutantCode': row['air_pollutant_code'],
                    'End': end_time,
                    'Value': row['value'],
                    'Unit': row['unit'],
                    'Validity': row['validity'] or '',
                    'Verification': row['verification'] or '',
                    'Data Capture': row['data_capture'] or '',
                    'Time Resolution': row['time_resolution'],
                    'Result Time': result_time
                })
        
        return U.csv_response(csv_buffer.getvalue(), f"MeasurementResult_{year}.csv")


@dataflow_endpoint.route("/api/dataflow/csv/zonegeometry", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_zonegeometry_csv():
    """Export zone geometry as CSV matching Reportnet3 format"""
    with CursorFromPool() as cursor:
        # Get country code from settings
        cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
        settings_row = cursor.fetchone()
        country_code = settings_row['country_code_id'] if settings_row else None
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                z.id as zone_id,
                ST_AsGeoJSON(ST_Multi(z.geom))::json AS zone_geometry
            FROM zones z
            ORDER BY z.id
        """, (country_code,))
        zones = cursor.fetchall()
        
        # Create CSV with proper headers and quoting
        csv_buffer = StringIO()
        if zones:
            fieldnames = ['Country Code', 'ZoneId', 'ZoneGeometry']
            writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            for row in zones:
                # Convert GeoJSON dict to Feature format with SRID property
                geojson = row['zone_geometry']
                feature = {
                    "type": "Feature",
                    "geometry": geojson,
                    "properties": {"srid": "4326"}
                }
                
                writer.writerow({
                    'Country Code': row['country_code'],
                    'ZoneId': row['zone_id'],
                    'ZoneGeometry': json.dumps(feature, separators=(',', ':'))
                })
        
        return U.csv_response(csv_buffer.getvalue(), "ZoneGeometry.csv")


@dataflow_endpoint.route("/api/dataflow/csv/download_all", methods=['POST'])
@jwt_required_with_exporting_claim()
def export_all_csv():
    """Export all dataflow CSVs as a ZIP file (optionally includes measurements for a specific year)"""
    data = request.get_json() or {}
    year = data.get('year')
    
    # Create a BytesIO buffer for the ZIP file
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Export authorities
        with CursorFromPool() as cursor:
            # Get country code from settings
            cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
            settings_row = cursor.fetchone()
            country_code = settings_row['country_code_id'] if settings_row else None
            
            cursor.execute("""
                SELECT 
                    %s as country_code,
                    a.id as authority_instance_id,
                    COALESCE(ao.notation, '') as object,
                    a.email,
                    COALESCE(ai.notation, '') as authority_instance,
                    a.organisation_name,
                    COALESCE(a.organisation_url, '') as organisation_url,
                    COALESCE(a.organisation_address, '') as organisation_address,
                    COALESCE(a.person_name, '') as person_name,
                    COALESCE(ast.notation, '') as authority_status
                FROM authorities a
                LEFT JOIN eea_authorityinstance ai ON a.instance_id = ai.id
                LEFT JOIN eea_authorityobject ao ON a.object_id = ao.id
                LEFT JOIN eea_authoritystatus ast ON a.status_id = ast.id
                ORDER BY a.id
            """, (country_code,))
            authorities = cursor.fetchall()
            
            if authorities:
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=[
                    'Country Code', 'Authority Instance Id', 'Object', 'Email',
                    'Authority Instance', 'Organisation Name', 'Organisation URL',
                    'Organisation Address', 'Person Name', 'Authority Status'
                ], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in authorities:
                    writer.writerow({
                        'Country Code': row['country_code'],
                        'Authority Instance Id': row['authority_instance_id'],
                        'Object': row['object'],
                        'Email': row['email'],
                        'Authority Instance': row['authority_instance'],
                        'Organisation Name': row['organisation_name'],
                        'Organisation URL': row['organisation_url'],
                        'Organisation Address': row['organisation_address'],
                        'Person Name': row['person_name'],
                        'Authority Status': row['authority_status']
                    })
                
                zip_file.writestr('Authority.csv', csv_buffer.getvalue())
        
        # Export stations
        with CursorFromPool() as cursor:
            # Get country code and timezone from settings
            cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
            settings_row = cursor.fetchone()
            country_code = settings_row['country_code_id'] if settings_row else None
            timezone_id = settings_row['timezone_id'] if settings_row else None
            
            cursor.execute("""
                SELECT 
                    %s as country_code,
                    s.eoi_code as air_quality_station_eoi_code,
                    s.network_id as air_quality_network,
                    n.name as air_quality_network_name,
                    al.notation as air_quality_network_organisational_level,
                    %s as timezone,
                    s.national_code as air_quality_station_nat_code,
                    s.name as aq_station_name,
                    n.report_id as network_report_id
                FROM stations s
                JOIN networks n ON s.network_id = n.id
                LEFT JOIN eea_administrativelevels al ON n.administration_level_id = al.id
                ORDER BY s.id
            """, (country_code, timezone_id))
            stations = cursor.fetchall()
            
            if stations:
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=[
                    'CountryCode', 'AirQualityStationEoICode', 'Air Quality Network',
                    'Air Quality Network Name', 'Air Quality Network Organisational Level',
                    'Timezone', 'Air Quality Station Nat Code', 'AQ Station Name', 
                    'NetworkReportId'
                ], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in stations:
                    writer.writerow({
                        'CountryCode': row['country_code'],
                        'AirQualityStationEoICode': row['air_quality_station_eoi_code'],
                        'Air Quality Network': row['air_quality_network'],
                        'Air Quality Network Name': row['air_quality_network_name'],
                        'Air Quality Network Organisational Level': row['air_quality_network_organisational_level'],
                        'Timezone': row['timezone'],
                        'Air Quality Station Nat Code': row['air_quality_station_nat_code'] or '',
                        'AQ Station Name': row['aq_station_name'],
                        'NetworkReportId': row['network_report_id'] or ''
                    })
                
                zip_file.writestr('Station.csv', csv_buffer.getvalue())
        
        # Export sampling points
        with CursorFromPool() as cursor:
            cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
            settings_row = cursor.fetchone()
            country_code = settings_row['country_code_id'] if settings_row else None
            
            cursor.execute("""
                SELECT 
                    %s as country_code,
                    sp.id as assessment_method_id,
                    sp.sampling_point_ref,
                    po.notation as air_pollutant_code,
                    st.eoi_code as air_quality_station_eoi_code,
                    ac.notation as air_quality_station_area,
                    sc.notation as air_quality_spo_category,
                    st.supersite as super_site,
                    st.latitude,
                    st.longitude,
                    st.altitude as altitude_masl,
                    sp.inlet_height as inlet_height_m,
                    sp.building_distance as building_distance_m,
                    sp.kerb_distance as kerb_distance_m,
                    sp.emission_source_distance as emission_source_distance_m
                FROM sampling_points sp
                JOIN stations st ON sp.station_id = st.id
                JOIN eea_pollutants po ON sp.pollutant_id = po.id
                LEFT JOIN eea_areaclassifications ac ON st.area_classification_id = ac.id
                LEFT JOIN eea_spocategory sc ON sp.spo_category_id = sc.id
                ORDER BY sp.id
            """, (country_code,))
            samplingpoints = cursor.fetchall()
            
            if samplingpoints:
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=[
                    'CountryCode', 'Assessment Method Id', 'Sampling Point Ref',
                    'AirPollutantCode', 'Air Quality Station Eo I Code', 
                    'Air Quality Station Area', 'AirQualitySPOCategory', 'Super Site',
                    'Latitude', 'Longitude', 'Altitude(masl)', 'InletHeight(m)',
                    'BuildingDistance(m)', 'KerbDistance(m)', 'EmissionSourceDistance(m)'
                ], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in samplingpoints:
                    writer.writerow({
                        'CountryCode': row['country_code'],
                        'Assessment Method Id': row['assessment_method_id'],
                        'Sampling Point Ref': row['sampling_point_ref'] or '',
                        'AirPollutantCode': row['air_pollutant_code'],
                        'Air Quality Station Eo I Code': row['air_quality_station_eoi_code'],
                        'Air Quality Station Area': row['air_quality_station_area'] or '',
                        'AirQualitySPOCategory': row['air_quality_spo_category'] or '',
                        'Super Site': 'true' if row['super_site'] else 'false',
                        'Latitude': row['latitude'],
                        'Longitude': row['longitude'],
                        'Altitude(masl)': row['altitude_masl'] or '',
                        'InletHeight(m)': row['inlet_height_m'] or '',
                        'BuildingDistance(m)': row['building_distance_m'] or '',
                        'KerbDistance(m)': row['kerb_distance_m'] or '',
                        'EmissionSourceDistance(m)': row['emission_source_distance_m'] or ''
                    })
                
                zip_file.writestr('SamplingPoint.csv', csv_buffer.getvalue())
        
        # Export processes
        with CursorFromPool() as cursor:
            cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
            settings_row = cursor.fetchone()
            country_code = settings_row['country_code_id'] if settings_row else None
            
            cursor.execute("""
                SELECT 
                    %s as country_code,
                    p.id as process_id,
                    sp.id as assessment_method_id,
                    p.activity_begin as process_activity_begin,
                    p.activity_end as process_activity_end,
                    po.notation as air_pollutant_code,
                    mt.notation as measurement_type,
                    mm.notation as method,
                    me.notation as equipment,
                    at.notation as analytical_technique,
                    ed.notation as equivalence_demonstrated,
                    p.data_quality_report_id,
                    p.equivalence_demonstration_report_id,
                    p.process_documentation_id
                FROM processes p
                JOIN sampling_points sp ON p.sampling_point_id = sp.id
                JOIN eea_pollutants po ON sp.pollutant_id = po.id
                LEFT JOIN eea_measurementtypes mt ON p.measurement_type_id = mt.id
                LEFT JOIN eea_measurementmethods mm ON p.method_id = mm.id
                LEFT JOIN eea_measurementequipments me ON p.equipment_id = me.id
                LEFT JOIN eea_analyticaltechnique at ON p.analytical_technique_id = at.id
                LEFT JOIN eea_equivalencedemonstrated ed ON p.equivalence_demonstrated_id = ed.id
                ORDER BY p.id
            """, (country_code,))
            processes = cursor.fetchall()
            
            if processes:
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=[
                    'CountryCode', 'Process Id', 'AssessmentMethodId',
                    'Process Activity Begin', 'Process Activity End', 'AirPollutantCode',
                    'Measurement Type', 'Method', 'Equipment', 'Analytical Technique',
                    'Equivalence Demonstrated', 'Data Quality Report Id',
                    'Equivalence Demonstration Report Id', 'Process Documentation Id'
                ], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for row in processes:
                    writer.writerow({
                        'CountryCode': row['country_code'],
                        'Process Id': row['process_id'],
                        'AssessmentMethodId': row['assessment_method_id'],
                        'Process Activity Begin': row['process_activity_begin'],
                        'Process Activity End': row['process_activity_end'] or '',
                        'AirPollutantCode': row['air_pollutant_code'],
                        'Measurement Type': row['measurement_type'] or '',
                        'Method': row['method'] or '',
                        'Equipment': row['equipment'] or '',
                        'Analytical Technique': row['analytical_technique'] or '',
                        'Equivalence Demonstrated': row['equivalence_demonstrated'] or '',
                        'Data Quality Report Id': row['data_quality_report_id'] or '',
                        'Equivalence Demonstration Report Id': row['equivalence_demonstration_report_id'] or '',
                        'Process Documentation Id': row['process_documentation_id'] or ''
                    })
                
                zip_file.writestr('SamplingPointProcess.csv', csv_buffer.getvalue())
        
        # Export measurements (if year is provided)
        if year:
            try:
                year_int = int(year)
                with CursorFromPool() as cursor:
                    cursor.execute("SELECT country_code_id, timezone_id FROM settings LIMIT 1")
                    settings_row = cursor.fetchone()
                    country_code = settings_row['country_code_id'] if settings_row else None
                    timezone_id = settings_row['timezone_id'] if settings_row else None
                    
                    # Get timezone offset (ISO 8601 format)
                    timezone_offset = ''
                    if timezone_id:
                        cursor.execute("SELECT timezone_offset FROM eea_timezones WHERE id = %s", (timezone_id,))
                        tz_row = cursor.fetchone()
                        timezone_offset = tz_row['timezone_offset'] if tz_row else ''
                    
                    cursor.execute("""
                        SELECT 
                            %s as country_code,
                            sp.id as assessment_method_id,
                            o.from_time,
                            po.notation as air_pollutant_code,
                            o.to_time,
                            o.value,
                            co.notation as unit,
                            ov.notation as validity,
                            ove.notation as verification,
                            NULL as data_capture,
                            tr.notation as time_resolution,
                            o.touched as result_time
                        FROM observations o
                        JOIN sampling_points sp ON o.sampling_point_id = sp.id
                        JOIN eea_pollutants po ON sp.pollutant_id = po.id
                        JOIN eea_concentrations co ON sp.unit_id = co.id
                        JOIN eea_times tr ON sp.time_resolution_id = tr.id
                        LEFT JOIN eea_observationvalidity ov ON o.observationvalidity_id = ov.id
                        LEFT JOIN eea_observationverification ove ON o.observationverification_id = ove.id
                        WHERE EXTRACT(YEAR FROM o.from_time) = %s
                        ORDER BY sp.id, o.from_time
                    """, (country_code, year_int))
                    measurements = cursor.fetchall()
                    
                    if measurements:
                        csv_buffer = StringIO()
                        writer = csv.DictWriter(csv_buffer, fieldnames=[
                            'CountryCode', 'AssessmentMethodId', 'Start', 'AirPollutantCode',
                            'End', 'Value', 'Unit', 'Validity', 'Verification',
                            'Data Capture', 'Time Resolution', 'Result Time'
                        ], quoting=csv.QUOTE_ALL)
                        writer.writeheader()
                        
                        for row in measurements:
                            start_time = row['from_time'].strftime('%Y-%m-%d %H:%M:%S')
                            end_time = row['to_time'].strftime('%Y-%m-%d %H:%M:%S')
                            result_time = row['result_time'].strftime('%Y-%m-%d %H:%M:%S')
                            
                            if timezone_offset:
                                start_time = f"{start_time}{timezone_offset}"
                                end_time = f"{end_time}{timezone_offset}"
                                result_time = f"{result_time}{timezone_offset}"
                            
                            writer.writerow({
                                'CountryCode': row['country_code'],
                                'AssessmentMethodId': row['assessment_method_id'],
                                'Start': start_time,
                                'AirPollutantCode': row['air_pollutant_code'],
                                'End': end_time,
                                'Value': row['value'],
                                'Unit': row['unit'],
                                'Validity': row['validity'] or '',
                                'Verification': row['verification'] or '',
                                'Data Capture': row['data_capture'] or '',
                                'Time Resolution': row['time_resolution'],
                                'Result Time': result_time
                            })
                        
                        zip_file.writestr(f'MeasurementResult_{year_int}.csv', csv_buffer.getvalue())
            except (ValueError, TypeError):
                pass  # Skip measurements if year is invalid
        
        # Export zone geometry
        with CursorFromPool() as cursor:
            cursor.execute("SELECT country_code_id FROM settings LIMIT 1")
            settings_row = cursor.fetchone()
            country_code = settings_row['country_code_id'] if settings_row else None
            
            cursor.execute("""
                SELECT 
                    %s as country_code,
                    z.id as zone_id,
                    ST_AsGeoJSON(ST_Multi(z.geom))::json AS zone_geometry
                FROM zones z
                ORDER BY z.id
            """, (country_code,))
            zones = cursor.fetchall()
            
            if zones:
                csv_buffer = StringIO()
                writer = csv.DictWriter(csv_buffer, fieldnames=[
                    'Country Code', 'ZoneId', 'ZoneGeometry'
                ], quoting=csv.QUOTE_ALL)
                writer.writeheader()
                
                for row in zones:
                    geojson = row['zone_geometry']
                    feature = {
                        "type": "Feature",
                        "geometry": geojson,
                        "properties": {"srid": "4326"}
                    }
                    
                    writer.writerow({
                        'Country Code': row['country_code'],
                        'ZoneId': row['zone_id'],
                        'ZoneGeometry': json.dumps(feature, separators=(',', ':'))
                    })
                
                zip_file.writestr('ZoneGeometry.csv', csv_buffer.getvalue())
    
    # Prepare the ZIP file for download
    zip_buffer.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    response = Response(zip_buffer.read(), mimetype='application/zip')
    response.headers['Content-Disposition'] = f'attachment; filename=dataflow_export_{timestamp}.zip'
    zip_buffer.close()
    
    return response


# OLD DATAFLOW ENDPOINTS (XML based - kept for backward compatibility)

@dataflow_endpoint.route('/api/dataflow', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows():
    m = DataflowModel(**request.args.to_dict())
    xml = Dataflows.get_xml(m.type, m.year, m.timezone, m.description)
    if xml == None:
        raise BadRequest("Could not create xml for dataflow " + m.type)

    return U.xmlify(xml)


@dataflow_endpoint.route('/api/dataflow/e2a', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_e2a():
    m = DataflowModelE2a(**request.args.to_dict())
    xml = Dataflows.get_dataflowE2A(m.last_request)
    if xml == None:
        raise BadRequest("Could not create xml for dataflow E2a")

    return U.xmlify(xml)


@dataflow_endpoint.route('/api/dataflow/reportnet3/csv', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"msg": "Reportnet3 dataflow is not enabled"}), 403

    m = DataflowModel(**request.args.to_dict())
    data = Dataflows_reportnet3.get_dataflow(m.type, m.year, m.timezone, m.description)
    if not data:
        raise BadRequest("Could not create csv for dataflow "+m.type+", no data found")

    # Create a zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if isinstance(data, list):
            # Convert data to a DataFrame and write it to a single CSV file
            df = pd.DataFrame(data)
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            zip_file.writestr("reportnet3_dataflow.csv", csv_buffer.getvalue())
        else:
            for filename, df in data.items():
                # Convert df to a DataFrame if it's a list
                if isinstance(df, list):
                    df = pd.DataFrame(df)
                # Convert each DataFrame to a CSV and add it to the zip file
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                zip_file.writestr(filename, csv_buffer.getvalue())

    # Get the bytes of the zip file
    zip_buffer.seek(0)

    # Create a Flask response and set the appropriate headers
    response = Response(zip_buffer.read(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename=reportnet3_dataflow.zip'
    zip_buffer.close()

    return response


@dataflow_endpoint.route('/api/dataflow/showreportnet3', methods=['GET'])
@jwt_required()
def show_reportnet3():
    return jsonify({"showreportnet3": current_app.config['SHOWREPORTNET3']})


@dataflow_endpoint.route('/api/dataflow/reportnet3/b', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_b():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"msg": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_dataflowB()
    if not data:
        raise BadRequest("No data for dataflow B found")

    return jsonify(data)


@dataflow_endpoint.route('/api/dataflow/reportnet3/d/processes', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_d_processes():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"msg": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_processes()
    if not data:
        raise BadRequest("No data for dataflow D Processes found")

    return jsonify(data)


@dataflow_endpoint.route('/api/dataflow/reportnet3/d/samplingpoints', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_d_samplingpoints():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"msg": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_samplingpoints()
    if not data:
        raise BadRequest("No data for dataflow D Samplingpoints found")

    return jsonify(data)
