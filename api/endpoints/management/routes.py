from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.networks.models import NetworkModel, DeleteModel
from api.core.query import Q


management_endpoint = Blueprint('management', __name__)

## LOOKUPS ##


@management_endpoint.route('/api/management/selects/areaclassifications', methods=['GET'])
@jwt_required()
def areaclassifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_areaclassifications r order by r.label")
        areaclassifications = cursor.fetchall()
        return jsonify(areaclassifications)


@management_endpoint.route('/api/management/selects/assessmentexceedances', methods=['GET'])
@jwt_required()
def exceedances():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from eea_assessmentthresholdexceedances r order by r.id")
        equivdemonstrations = cursor.fetchall()
        return jsonify(equivdemonstrations)


@management_endpoint.route('/api/management/selects/assessmenttypes', methods=['GET'])
@jwt_required()
def assessmenttypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_assessmenttypes r order by r.label")
        assessmenttypes = cursor.fetchall()
        return jsonify(assessmenttypes)


@management_endpoint.route('/api/management/selects/authorities', methods=['GET'])
@jwt_required()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/selects/concentrations', methods=['GET'])
@jwt_required()
def concentrations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_concentrations r order by r.label")
        concentrations = cursor.fetchall()
        return jsonify(concentrations)


@management_endpoint.route('/api/management/selects/equivdemonstrations', methods=['GET'])
@jwt_required()
def equivdemonstrations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_equivalencedemonstrated r order by r.label")
        equivdemonstrations = cursor.fetchall()
        return jsonify(equivdemonstrations)


@management_endpoint.route('/api/management/selects/levels', methods=['GET'])
@jwt_required()
def levels():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_organisationallevels r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/selects/media', methods=['GET'])
@jwt_required()
def media():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_mediavalues r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@management_endpoint.route('/api/management/selects/measurementequipment', methods=['GET'])
@jwt_required()
def measurementequipment():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementequipments r order by r.label")
        measurementequipment = cursor.fetchall()
        return jsonify(measurementequipment)


@management_endpoint.route('/api/management/selects/measurementmethods', methods=['GET'])
@jwt_required()
def measurement_methods():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementmethods r order by r.label")
        measurement_methods = cursor.fetchall()
        return jsonify(measurement_methods)


@management_endpoint.route('/api/management/selects/measurementregimes', methods=['GET'])
@jwt_required()
def measurementregimes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementregimevalues r order by r.label")
        measurementregimes = cursor.fetchall()
        return jsonify(measurementregimes)


@management_endpoint.route('/api/management/selects/measurementtypes', methods=['GET'])
@jwt_required()
def measurementtypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementtypes r order by r.label")
        measurementtypes = cursor.fetchall()
        return jsonify(measurementtypes)


@management_endpoint.route('/api/management/selects/network', methods=['GET'])
@jwt_required()
def networks():
    with CursorFromPool() as cursor:
        cursor.execute("select n.name as label, n.id as value from networks n order by n.name")
        networks = cursor.fetchall()
        return jsonify(networks)


@management_endpoint.route('/api/management/selects/pollutants', methods=['GET'])
@jwt_required()
def pollutants():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.uri as value from eea_pollutants r order by r.label")
        pollutants = cursor.fetchall()
        return jsonify(pollutants)


@management_endpoint.route('/api/management/selects/processes', methods=['GET'])
@jwt_required()
def processes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from processes r order by r.id")
        processes = cursor.fetchall()
        return jsonify(processes)


@management_endpoint.route('/api/management/selects/processtypevalues', methods=['GET'])
@jwt_required()
def processtypevalues():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_processtypevalues r order by r.label")
        processtypevalues = cursor.fetchall()
        return jsonify(processtypevalues)


@management_endpoint.route('/api/management/selects/responsibleauthorities', methods=['GET'])
@jwt_required()
def responsibleauthorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        responsibleauthorities = cursor.fetchall()
        return jsonify(responsibleauthorities)


@management_endpoint.route('/api/management/selects/resultnaturevalues', methods=['GET'])
@jwt_required()
def resultnaturevalues():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_resultnaturevalues r order by r.label")
        resultnaturevalues = cursor.fetchall()
        return jsonify(resultnaturevalues)


@management_endpoint.route('/api/management/selects/samplingpoints', methods=['GET'])
@jwt_required()
def samplingpoints():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from sampling_points r order by r.id")
        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@management_endpoint.route('/api/management/selects/samples', methods=['GET'])
@jwt_required()
def samples():
    with CursorFromPool() as cursor:
        cursor.execute("select r.id as label, r.id as value from samples r order by r.id")
        samples = cursor.fetchall()
        return jsonify(samples)


@management_endpoint.route('/api/management/selects/stations', methods=['GET'])
@jwt_required()
def stations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from stations r order by r.name")
        stations = cursor.fetchall()
        return jsonify(stations)


@management_endpoint.route('/api/management/selects/stationclassifications', methods=['GET'])
@jwt_required()
def station_classifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_stationclassifications r order by r.label")
        station_classifications = cursor.fetchall()
        return jsonify(station_classifications)


@management_endpoint.route('/api/management/selects/timezones', methods=['GET'])
@jwt_required()
def timezones():
    timezones = Q.timezones()
    return jsonify(timezones)


@management_endpoint.route('/api/management/selects/timesteps', methods=['GET'])
@jwt_required()
def timesteps():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_times r order by r.label")
        timesteps = cursor.fetchall()
        return jsonify(timesteps)


@management_endpoint.route('/api/management/selects/zones', methods=['GET'])
@jwt_required()
def zones():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from zones r order by r.name")
        zones = cursor.fetchall()
        return jsonify(zones)
