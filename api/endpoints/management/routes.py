from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.networks.models import NetworkModel, DeleteModel
from api.core.query import Q


management_endpoint = Blueprint('management', __name__)

## LOOKUPS ##


@management_endpoint.route('/api/management/selects/network', methods=['GET'])
@jwt_required()
def networks():
    with CursorFromPool() as cursor:
        cursor.execute("select n.name as label, n.id as value from networks n order by n.name")
        networks = cursor.fetchall()
        return jsonify(networks)


@management_endpoint.route('/api/management/selects/authorities', methods=['GET'])
@jwt_required()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


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


@management_endpoint.route('/api/management/selects/timezones', methods=['GET'])
@jwt_required()
def timezones():
    timezones = Q.timezones()
    return jsonify(timezones)


@management_endpoint.route('/api/management/selects/measurementregimes', methods=['GET'])
@jwt_required()
def measurementregimes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_measurementregimevalues r order by r.label")
        measurementregimes = cursor.fetchall()
        return jsonify(measurementregimes)


@management_endpoint.route('/api/management/selects/areaclassifications', methods=['GET'])
@jwt_required()
def areaclassifications():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_areaclassifications r order by r.label")
        areaclassifications = cursor.fetchall()
        return jsonify(areaclassifications)


@management_endpoint.route('/api/management/selects/assessmenttypes', methods=['GET'])
@jwt_required()
def assessmenttypes():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_assessmenttypes r order by r.label")
        assessmenttypes = cursor.fetchall()
        return jsonify(assessmenttypes)


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


@management_endpoint.route('/api/management/selects/pollutants', methods=['GET'])
@jwt_required()
def pollutants():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.uri as value from eea_pollutants r order by r.label")
        pollutants = cursor.fetchall()
        return jsonify(pollutants)


@management_endpoint.route('/api/management/selects/concentrations', methods=['GET'])
@jwt_required()
def concentrations():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_concentrations r order by r.label")
        concentrations = cursor.fetchall()
        return jsonify(concentrations)


@management_endpoint.route('/api/management/selects/timesteps', methods=['GET'])
@jwt_required()
def timesteps():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_times r order by r.label")
        timesteps = cursor.fetchall()
        return jsonify(timesteps)


@management_endpoint.route('/api/management/selects/assessment_types', methods=['GET'])
@jwt_required()
def assessment_types():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_assessmenttypes r order by r.label")
        assessment_types = cursor.fetchall()
        return jsonify(assessment_types)
