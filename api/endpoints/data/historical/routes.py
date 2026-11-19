from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.data.historical.models import HistoricalModel
from core.data.mean import Mean, MeanType
from core.jwt_ext_custom import jwt_required_with_data_claim
from core.query import Q

historical_endpoint = Blueprint('historical', __name__)


@historical_endpoint.route('/api/data/historical', methods=['POST'])
@jwt_required_with_data_claim()
def historical():
    with CursorFromPool() as cursor:
        m = HistoricalModel(**request.json)
        sampling_point_ids = Q.sampling_point_ids_by_networks_access(m.sampling_point_ids)
        # pluginMetadata: series with a local (plugin) pollutant or unit get their name and
        # unit in the legend and table, and their own y-axis, like on the dashboard.
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True, pluginMetadata=True)
        return jsonify(meanvalues)


## LOOKUPS ##

@historical_endpoint.route('/api/data/historical/timeseries', methods=['GET'])
@jwt_required_with_data_claim()
def timeseries():
    timeseries = Q.timeseries_columns_with_time_by_access()
    return jsonify(timeseries)
