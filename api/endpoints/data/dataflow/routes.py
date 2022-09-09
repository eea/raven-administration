from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from api.core.database import CursorFromPool
from api.core.query import Q
from api.core.utils import U


dataflow_endpoint = Blueprint('dataflow', __name__)


@dataflow_endpoint.route('/api/data/dataflow/timezones', methods=['GET'])
@jwt_required()
def timezones():
    timezones = Q.timezones()
    return jsonify(timezones)


@dataflow_endpoint.route('/api/data/dataflow/test', methods=['GET'])
def test():
    xml = {"hello": "world"}
    return U.xmlify(xml)
