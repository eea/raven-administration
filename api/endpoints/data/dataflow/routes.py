from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.query import Q
from core.utils import U
from endpoints.data.dataflow.models import DataflowModel, DataflowModelE2a
from core.eea.dataflows import Dataflows
from core.jwt_ext_custom import jwt_required_with_exporting_claim

dataflow_endpoint = Blueprint('dataflow', __name__)


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
