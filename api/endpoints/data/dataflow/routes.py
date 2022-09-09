from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.query import Q
from api.core.utils import U
from api.endpoints.data.dataflow.models import DataflowModel, DataflowModelE2a
from api.core.eea.dataflows import Dataflows


dataflow_endpoint = Blueprint('dataflow', __name__)


@dataflow_endpoint.route('/api/dataflow', methods=['GET'])
def dataflows():
    m = DataflowModel(**request.args.to_dict())
    xml = Dataflows.get_xml(m.type, m.year, m.timezone, m.description)
    if xml == None:
        raise BadRequest("Could not create xml for dataflow " + m.type)

    return U.xmlify(xml)


@dataflow_endpoint.route('/api/dataflow/e2a', methods=['GET'])
def dataflows_e2a():
    m = DataflowModelE2a(**request.args.to_dict())
    xml = Dataflows.get_dataflowE2A(m.last_request)
    if xml == None:
        raise BadRequest("Could not create xml for dataflow E2a")

    return U.xmlify(xml)
