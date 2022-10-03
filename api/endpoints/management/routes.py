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
