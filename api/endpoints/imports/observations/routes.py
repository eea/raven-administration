from datetime import datetime
from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest, InternalServerError
from api.core.database import CursorFromPool
from api.core.printcol import printcol
from api.core.data.processing.importing import Importing
import io
import pandas as pd
import time
from api.endpoints.imports.observations.models import LoggerValues, LoggerLastValue
from pandas import DataFrame

observations_endpoint = Blueprint('observations', __name__)


@observations_endpoint.route('/api/imports/observations', methods=['POST'])
# @jwt_required()
def import_obs():
    with CursorFromPool() as cursor:
        bench = time.perf_counter()

        # Read csv into a pandas DataFrame
        f = request.files["csv"]
        df = pd.read_csv(io.StringIO(f.stream.read().decode("utf-8")))

        # Import values
        Importing.Import(cursor, df)

        printcol(f"- Total time used {time.perf_counter() - bench} seconds")
    return jsonify({"success": True})


@observations_endpoint.route('/api/imports/logger', methods=['POST'])
# @jwt_required()
def import_logger():
    with CursorFromPool() as cursor:
        bench = time.perf_counter()
        # Read list into a pandas DataFrame
        df = DataFrame(request.json['values'])

        if not len(set(df.logger_id.tolist())) == 1:
            raise Exception("Only one logger_id at a time allowed")

        # Convert logger df to import df
        logger_id = df.logger_id[0]
        sampling_point_id = None

        sql = """
            select sp.id
            from sampling_points sp
            where sp.logger_id = %(id)s
        """
        cursor.execute(sql, {"id": logger_id})
        sp_row = cursor.fetchone()
        sampling_point_id = sp_row["id"]
        if sampling_point_id == None:
            raise Exception("Could not find logger id")

        df["logger_id"] = sampling_point_id
        df["verification_flag"] = 3
        df["validation_flag"] = 1
        df.loc[df['validity'] < 75, 'validation_flag'] = -1  # if validity is below 75, make it not valid

        df = df.rename(columns={"fromTime": "begin_position", "toTime": "end_position", "logger_id": "sampling_point_id"})

        df.drop(['validity'], axis=1)
        df.reset_index(drop=True)

        # Import values
        Importing.Import(cursor, df)

        printcol(f"- Total time used {time.perf_counter() - bench} seconds")
    return jsonify({"success": True})


@observations_endpoint.route('/api/imports/logger', methods=['GET'])
# @jwt_required()
def last_entry():
    with CursorFromPool() as cursor:
        m = LoggerLastValue(**request.args.to_dict())
        sql = """
			      select to_char(s.to_time,'yyyy-mm-dd HH24:mi:ss') as "lastEntry"
            from sampling_points s
            where s.logger_id = %(id)s
        """
        cursor.execute(sql, m)
        values = cursor.fetchone()
        return jsonify(values)
