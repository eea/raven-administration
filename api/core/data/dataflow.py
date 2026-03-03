"""
Reportnet3 CSV Dataflow Exports
Reusable functions for generating CSV exports in Reportnet3 format
"""
from io import StringIO
import csv
import json
from core.database import CursorFromPool


def get_authorities_csv(country_code):
    """Generate Authority CSV export"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT 
                %s as country_code,
                a.id as authority_instance_id,
                ai.notation as object,
                a.email,
                ai.label as authority_instance,
                a.organisation_name,
                a.organisation_url,
                a.organisation_address,
                a.person_name,
                ais.notation as authority_status
            FROM authorities a
            LEFT JOIN eea_authorityinstance ai ON a.authority_instance_id = ai.id
            LEFT JOIN eea_authoritystatus ais ON a.authority_status_id = ais.id
            ORDER BY a.id
        """, (country_code,))
        authorities = cursor.fetchall()
        
        if not authorities:
            return ""
        
        csv_buffer = StringIO()
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
                'Organisation URL': row['organisation_url'] or '',
                'Organisation Address': row['organisation_address'] or '',
                'Person Name': row['person_name'] or '',
                'Authority Status': row['authority_status']
            })
        
        return csv_buffer.getvalue()


def get_stations_csv(country_code, timezone_id):
    """Generate Station CSV export"""
    with CursorFromPool() as cursor:
        # Get timezone notation
        timezone_notation = ''
        if timezone_id:
            cursor.execute("SELECT notation FROM eea_timezones WHERE id = %s", (timezone_id,))
            tz_row = cursor.fetchone()
            timezone_notation = tz_row['notation'] if tz_row else ''
        
        cursor.execute("""
            SELECT 
                %s as country_code,
                s.eoi_code as air_quality_station_eoi_code,
                ac.notation as air_quality_station_area,
                st.notation as air_quality_station_type,
                n.eoi_code as air_quality_network,
                n.name as air_quality_network_name,
                al.notation as air_quality_network_organisational_level,
                %s as timezone,
                s.national_code as air_quality_station_nat_code,
                s.name as aq_station_name,
                s.network_report_id
            FROM stations s
            JOIN networks n ON s.network_id = n.id
            LEFT JOIN eea_areaclassifications ac ON s.area_classification_id = ac.id
            LEFT JOIN eea_stationtypes st ON s.station_type_id = st.id
            LEFT JOIN eea_administrativelevels al ON n.administration_level_id = al.id
            ORDER BY s.eoi_code
        """, (country_code, timezone_notation))
        stations = cursor.fetchall()
        
        if not stations:
            return ""
        
        csv_buffer = StringIO()
        fieldnames = [
            'Country Code', 'Air Quality Station Eo I Code', 'Air Quality Station Area',
            'Air Quality Station Type', 'Air Quality Network', 'Air Quality Network Name',
            'Air Quality Network Organisational Level', 'Timezone',
            'Air Quality Station Nat Code', 'AQ Station Name', 'NetworkReportId'
        ]
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for row in stations:
            writer.writerow({
                'Country Code': row['country_code'],
                'Air Quality Station Eo I Code': row['air_quality_station_eoi_code'],
                'Air Quality Station Area': row['air_quality_station_area'],
                'Air Quality Station Type': row['air_quality_station_type'],
                'Air Quality Network': row['air_quality_network'],
                'Air Quality Network Name': row['air_quality_network_name'],
                'Air Quality Network Organisational Level': row['air_quality_network_organisational_level'],
                'Timezone': row['timezone'],
                'Air Quality Station Nat Code': row['air_quality_station_nat_code'] or '',
                'AQ Station Name': row['aq_station_name'],
                'NetworkReportId': row['network_report_id'] or ''
            })
        
        return csv_buffer.getvalue()


def get_samplingpoints_csv(country_code):
    """Generate SamplingPoint CSV export"""
    with CursorFromPool() as cursor:
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
        
        if not samplingpoints:
            return ""
        
        csv_buffer = StringIO()
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
        
        return csv_buffer.getvalue()


def get_processes_csv(country_code):
    """Generate SamplingPointProcess CSV export"""
    with CursorFromPool() as cursor:
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
        
        if not processes:
            return ""
        
        csv_buffer = StringIO()
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
        
        return csv_buffer.getvalue()


def get_measurements_csv(country_code, timezone_id, year):
    """Generate MeasurementResult CSV export for a specific year"""
    with CursorFromPool() as cursor:
        # Get timezone offset
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
        
        if not measurements:
            return ""
        
        csv_buffer = StringIO()
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
        
        return csv_buffer.getvalue()


def get_zonegeometry_csv(country_code):
    """Generate ZoneGeometry CSV export"""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT 
                %s as country_code,
                z.id as zone_id,
                ST_AsGeoJSON(ST_Multi(z.geom))::json AS zone_geometry
            FROM zones z
            ORDER BY z.id
        """, (country_code,))
        zones = cursor.fetchall()
        
        if not zones:
            return ""
        
        csv_buffer = StringIO()
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
        
        return csv_buffer.getvalue()
