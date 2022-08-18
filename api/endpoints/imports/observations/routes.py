from datetime import datetime
from email.utils import parsedate_to_datetime
from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest, InternalServerError
from api.core.database import CursorFromPool
from api.core.printcol import printcol
from api.endpoints.imports.observations.models import Processvalues
from api.core.data.processing.importing import Importing
import io
import pandas as pd
import pandera as pa
import numpy as np
from pandera import Column, DataFrameSchema, Check, Index
import time

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
    return jsonify({"hey": "ho"})
