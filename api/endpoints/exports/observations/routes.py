from flask import jsonify, Blueprint, request, Response
from core.database import CursorFromPool
from core.data.management import Management
from core.jwt_ext_custom import jwt_required_with_data_claim
from endpoints.exports.observations.models import ObservationModel
from core.query import Q
from core.utils import U
from core.data.mean import Mean, MeanType
import pandas as pd

export_observations_endpoint = Blueprint('export_observations', __name__)


@export_observations_endpoint.route('/api/exports/observations', methods=['POST'])
@jwt_required_with_data_claim()
def historical():
    with CursorFromPool() as cursor:
        m = ObservationModel(**request.json)
        sampling_point_ids = Q.sampling_point_ids_by_networks_access(m.sampling_point_ids)
        meanvalues = Mean.Aggregate(cursor, MeanType(m.meantype), sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True)
        df = pd.DataFrame.from_records(meanvalues)
        return U.dataframe_to_csv_response(df, "observations.csv")
