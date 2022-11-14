from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.data.historical.models import HistoricalModel
from api.core.data.mean import Mean, MeanType
from api.core.jwt_ext_custom import jwt_required_with_data_claim
from api.core.query import Q

historical_endpoint = Blueprint('historical', __name__)


@historical_endpoint.route('/api/data/historical', methods=['POST'])
@jwt_required_with_data_claim()
def historical():
    with CursorFromPool() as cursor:
        m = HistoricalModel(**request.json)
        sampling_point_ids = Q.sampling_point_ids_by_networks_access(m.sampling_point_ids)
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True)
        return jsonify(meanvalues)


## LOOKUPS ##

@historical_endpoint.route('/api/data/historical/timeseries', methods=['GET'])
@jwt_required_with_data_claim()
def timeseries():
    timeseries = Q.timeseries_with_time_by_access()
    return jsonify(timeseries)
