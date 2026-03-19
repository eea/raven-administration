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
        meantype = MeanType(m.meantype)
        meanvalues = Mean.Aggregate(cursor, meantype, sampling_point_ids, m.from_dt, m.to_dt, m.coverage, 3, 3, True)
        df = pd.DataFrame.from_records(meanvalues)
        df_sorted = df.sort_values(["sampling_point_id", "datetime"])

        is_raw_or_original = meantype in (MeanType.Raw, MeanType.Original)
        if is_raw_or_original:
            df_out = df_sorted[["network", "station", "component", "unit", "timestep", "equipment", "equipment_identifier", "datetime_begin", "datetime", "actual_value", "valid"]]
            df_out = df_out.rename(columns={"component": "pollutant", "datetime_begin": "fromtime", "datetime": "totime", "actual_value": "value"})
        else:
            df_out = df_sorted[["network", "station", "component", "unit", "meantype_string", "equipment", "equipment_identifier", "datetime", "actual_value", "coverage", "valid"]]
            df_out = df_out.rename(columns={"component": "pollutant", "meantype_string": "timestep", "actual_value": "value"})

        return U.dataframe_to_csv_response(df_out, "observations.csv")
