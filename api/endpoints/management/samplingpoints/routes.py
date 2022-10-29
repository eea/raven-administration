from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.samplingpoints.models import SamplingPointsModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_observations_claim


samplingpoints_endpoint = Blueprint('samplingpoints', __name__)


@samplingpoints_endpoint.route('/api/management/samplingpoints', methods=['GET'])
@jwt_required_with_observations_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                sp.*,
                mv.label as media_monitored_name,
                st.name as station,
                mr.label as measurement_regime_name,
                ast.label as assessment_type_name,
                sc.label as station_classification_name,
                p.notation as pollutant_name,
                cn.notation as concentration_name,
                tm.label as timestep_name
            FROM sampling_points sp
                LEFT OUTER JOIN eea_mediavalues mv ON lower(sp.media_monitored) = lower(mv.id)
                LEFT OUTER JOIN eea_measurementregimevalues mr ON lower(sp.measurement_regime) = lower(mr.id)
                LEFT OUTER JOIN eea_assessmenttypes ast ON lower(sp.assessment_type) = lower(ast.id)
                LEFT OUTER JOIN eea_stationclassifications sc ON lower(sp.station_classification) = lower(sc.id),
                stations st, eea_pollutants p, eea_concentrations cn, eea_times tm
            WHERE sp.station_id = st.id
            AND sp.pollutant = p.uri
            AND sp.concentration = cn.id
            AND sp.timestep = tm.id
        """)
        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@samplingpoints_endpoint.route('/api/management/samplingpoints/update', methods=['POST'])
@jwt_required_with_observations_claim()
def samplingpoints_update():
    with CursorFromPool() as cursor:
        model = SamplingPointsModel(**request.json)
        sql = """
          INSERT INTO sampling_points 
            (id, media_monitored, station_id, measurement_regime, mobile, assessment_type, station_classification, used_aqd, 
            main_emission_sources, traffic_emissions, heating_emissions, industrial_emissions, distance_source, 
            change_aei_stations, begin_position, end_position, logger_id, pollutant, concentration, timestep)
                  VALUES (%(id)s, %(media_monitored)s, %(station_id)s, %(measurement_regime)s, %(mobile)s, 
            %(assessment_type)s, %(station_classification)s, %(used_aqd)s, %(main_emission_sources)s, 
            %(traffic_emissions)s, %(heating_emissions)s, %(industrial_emissions)s, %(distance_source)s,
            %(change_aei_stations)s, %(begin_position)s, %(end_position)s, %(logger_id)s, %(pollutant)s, %(concentration)s, %(timestep)s)
          ON CONFLICT (id) DO 
          UPDATE SET media_monitored=%(media_monitored)s, 
            station_id=%(station_id)s, 
            measurement_regime=%(measurement_regime)s, 
            mobile=%(mobile)s, 
            assessment_type=%(assessment_type)s, 
            station_classification=%(station_classification)s, 
            used_aqd=%(used_aqd)s, 
            main_emission_sources=%(main_emission_sources)s, 
            traffic_emissions=%(traffic_emissions)s, 
            heating_emissions=%(heating_emissions)s, 
            industrial_emissions=%(industrial_emissions)s, 
            distance_source=%(distance_source)s, 
            change_aei_stations=%(change_aei_stations)s, 
            begin_position=%(begin_position)s, 
            end_position=%(end_position)s,
            logger_id=%(logger_id)s,
            pollutant=%(pollutant)s,
            concentration=%(concentration)s,
            timestep=%(timestep)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@samplingpoints_endpoint.route('/api/management/samplingpoints/delete', methods=['POST'])
@jwt_required_with_observations_claim()
def samplingpoints_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = """
          delete from sampling_points where id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
