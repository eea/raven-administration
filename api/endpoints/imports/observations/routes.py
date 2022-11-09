from datetime import datetime
from email.utils import parsedate_to_datetime
from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest, InternalServerError
from api.core.database import CursorFromPool
from api.core.printcol import printcol
from api.core.data.processing.importing import Importing
import io
import pandas as pd
import time
from api.endpoints.imports.observations.model import LoggerValues, LoggerLastValue
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
			      select to_char(s.to_time,'yyyy-mm-dd HH24:mi:ss') as to_time
            from sampling_points s
            where s.logger_id = %(id)s
        """
        cursor.execute(sql, m)
        values = cursor.fetchone()
        return jsonify(values)
