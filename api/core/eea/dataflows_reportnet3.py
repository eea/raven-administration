from core.database import CursorFromPool
from core.eea.zone import Zone
from core.eea.dataflows import Dataflows

class Dataflows_reportnet3:
    
    @staticmethod
    def get_dataflow(type: str, year: int, timezone: str, description: str):
        if type.upper() == "B":
            return Dataflows_reportnet3.get_dataflowB()
        # if type.upper() == "C":
        #     return Dataflows.get_dataflowC(year, timezone, description)
        if type.upper() == "D":
            return Dataflows_reportnet3.get_dataflowD(year, timezone, description)
        # if type.upper() == "E1A":
        #     return Dataflows.get_dataflowE1A(year, timezone, description)
        # if type.upper() == "G":
        #     return Dataflows.get_dataflowG(year, timezone, description)
        return None

    @staticmethod
    def get_dataflowB():
        with CursorFromPool() as cursor:
            cursor.execute("""
              SELECT z."id",
                    z."name" AS zone_name,
                    z.code   AS zone_id,
                    z.area   AS zone_area,
                    to_timestamp(z.year::text || '-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS') AT TIME ZONE 'UTC' AS start_time,
                    (
                        SELECT json_build_object(
                                        'type', 'FeatureCollection',
                                        'features', json_agg(
                                                json_build_object(
                                                        'type', 'Feature',
                                                        'properties', json_build_object(
                                                                'srid', '4326'
                                                            ),
                                                        'geometry', ST_AsGeoJSON(z2.geom)::json
                                                    )
                                            )
                                    ) AS geometry
                        FROM zones z2
                        WHERE z2.id = z.id
                    )        AS geometry
              FROM zones z
              ORDER BY z.code;

              """)
            rows = cursor.fetchall()
            return rows
        
    @staticmethod
    def get_dataflowD(year: int, timezone: int, description: str):
        processes = Dataflows_reportnet3.get_processes()
        sampling_points = Dataflows_reportnet3.get_samplingpoints()

        return {            
            "processes.csv": processes,
            "sampling_points.csv": sampling_points
        } 

    
    @staticmethod
    def get_processes():
        with CursorFromPool() as cursor:
            cursor.execute("""
                select p.id as process_id,
                      p.id as process_name,
                      equiv_demonstration as equivalence_demo,
                      measurement_type,
                      measurement_method,
                      sampling_method,
                      analytical_tech as analytical_technique,
                      sampling_equipment,
                      measurement_equipment,
                      detection_limit,
                      detection_limit_uom as detection_limit_unit,
                      uncertainty_estimate,
                      documentation,
                      qa_report,
                      duration_number as measurement_duration_value,
                      duration_unit as measurement_duration_unit,
                      cadence_number as measurement_interval_value,
                      cadence_unit as measurement_interval_unit
                from processes p
            """)
            rows = cursor.fetchall()
            return rows

    @staticmethod
    def get_samplingpoints():
        with CursorFromPool() as cursor:
            cursor.execute("""
              select sp.id                     as samplingpoint_local_id,
                    sp.pollutant_id            as pollutant,
                    sp.id                     as samplingpoint_name,
                    sp.from_time              as start_date_time,
                    sp.to_time                as end_date_time,
                    sp.station_id             as station_local_id,
                    s.name                    as station_name,
                    s.city,
                    s.eoi_code                as eoi_site_id,
                    s.national_station_code,
                    ST_Y(s.geom)              as latitude,
                    ST_X(s.geom)              as longitude,
                    ST_Z(s.geom)              as altitude,
                    s.area_classification,
                    sp.station_classification as station_type,
                    s.network_id              as network_local_id,
                    n.name                    as network_name,
                    n.organisational          as organisationallevel,
                    n.aggregation_timezone    as aggregation_time_zone,
                    sp.assessment_type        as intended_assessment_type,
                    --sp. as process
                    sp.distance_source,
                    sp.main_emission_sources
              from sampling_points sp
                      left join stations s on sp.station_id = s.id
                      left join networks n on s.network_id = n.id
              """)
            rows = cursor.fetchall()
            return rows