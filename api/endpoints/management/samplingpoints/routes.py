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
                sp.id,
                sp.station_classification as station_classification_id,
                sp.assessment_type as assessment_type_id,
                sp.media_monitored as media_id,
                sp.station_id,
                sp.measurement_regime as measurement_regime_id,
                sp.end_position,
                sp.begin_position,
                sp.pollutant as pollutant_id,
                sp.timestep as timestep_id,
                sp.concentration as concentration_id,
                sp.main_emission_sources,
                sp.change_aei_stations,
                sp.distance_source,
                sp.industrial_emissions,
                sp.logger_id,
                sp.mobile,
                sp.heating_emissions,
                sp.traffic_emissions,
                sp.used_aqd,
                mv.label as media,
                st.name as station,
                mr.label as measurement_regime,
                ast.label as assessment_type,
                sc.label as station_classification,
                p.notation as pollutant,
                cn.notation as concentration,
                tm.label as timestep,tm.label,cn.notation
            FROM
                sampling_points sp,eea_mediavalues mv, eea_measurementregimevalues mr, eea_assessmenttypes ast,
                eea_stationclassifications sc, stations st, eea_pollutants p, eea_concentrations cn, eea_times tm
            WHERE sp.station_id = st.id
            AND sp.pollutant = p.uri
            AND sp.concentration = cn.id
            AND sp.timestep = tm.id
            AND sp.media_monitored = mv.id
            AND sp.measurement_regime = mr.id
            AND sp.assessment_type = ast.id
            AND sp.station_classification = sc.id
            ORDER BY st.name, p.notation
        """)
        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@samplingpoints_endpoint.route('/api/management/samplingpoints/update', methods=['POST'])
@jwt_required_with_observations_claim()
def samplingpoints_update():
    with CursorFromPool() as cursor:
        model = SamplingPointsModel(**request.json)
        sql = """ 
          UPDATE sampling_points
          SET 
            media_monitored=%(media_id)s, 
            station_id=%(station_id)s, 
            measurement_regime=%(measurement_regime_id)s, 
            mobile=%(mobile)s, 
            assessment_type=%(assessment_type_id)s, 
            station_classification=%(station_classification_id)s, 
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
            pollutant=%(pollutant_id)s,
            concentration=%(concentration_id)s,
            timestep=%(timestep_id)s
          WHERE id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@samplingpoints_endpoint.route('/api/management/samplingpoints/insert', methods=['POST'])
@jwt_required_with_observations_claim()
def samplingpoints_insert():
    with CursorFromPool() as cursor:
        model = SamplingPointsModel(**request.json)
        sql = """
          INSERT INTO sampling_points (
            id, 
            media_monitored, 
            station_id, 
            measurement_regime, 
            mobile, assessment_type, 
            station_classification, 
            used_aqd, 
            main_emission_sources, 
            traffic_emissions, 
            heating_emissions, 
            industrial_emissions, 
            distance_source, 
            change_aei_stations, 
            begin_position, 
            end_position, 
            logger_id, 
            pollutant, 
            concentration, 
            timestep
          )
          VALUES (
            %(id)s, 
            %(media_id)s, 
            %(station_id)s, 
            %(measurement_regime_id)s, 
            %(mobile)s, 
            %(assessment_type_id)s, 
            %(station_classification_id)s, 
            %(used_aqd)s, 
            %(main_emission_sources)s, 
            %(traffic_emissions)s, 
            %(heating_emissions)s, 
            %(industrial_emissions)s, 
            %(distance_source)s,
            %(change_aei_stations)s, 
            %(begin_position)s, 
            %(end_position)s, 
            %(logger_id)s,
            %(pollutant_id)s, 
            %(concentration_id)s, 
            %(timestep_id)s
          )           
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@samplingpoints_endpoint.route('/api/management/samplingpoints/delete', methods=['POST'])
@jwt_required_with_observations_claim()
def samplingpoints_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from sampling_points where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
