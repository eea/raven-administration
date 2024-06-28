from flask import jsonify, Blueprint, request, current_app, Response
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.query import Q
from core.utils import U
from endpoints.data.dataflow.models import DataflowModel, DataflowModelE2a
from core.eea.dataflows import Dataflows
from core.eea.dataflows_reportnet3 import Dataflows_reportnet3
from core.jwt_ext_custom import jwt_required_with_exporting_claim
import zipfile
from io import BytesIO
import pandas as pd

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


@dataflow_endpoint.route('/api/dataflow/reportnet3/csv', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"error": "Reportnet3 dataflow is not enabled"}), 403

    m = DataflowModel(**request.args.to_dict())
    data = Dataflows_reportnet3.get_dataflow(m.type, m.year, m.timezone, m.description)
    if not data:
        raise BadRequest("Could not create csv for dataflow "+m.type+", no data found")

    # Create a zip file in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if isinstance(data, list):
            # Convert data to a DataFrame and write it to a single CSV file
            df = pd.DataFrame(data)
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            zip_file.writestr("reportnet3_dataflow.csv", csv_buffer.getvalue())
        else:
            for filename, df in data.items():
                # Convert df to a DataFrame if it's a list
                if isinstance(df, list):
                    df = pd.DataFrame(df)
                # Convert each DataFrame to a CSV and add it to the zip file
                csv_buffer = BytesIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                zip_file.writestr(filename, csv_buffer.getvalue())

    # Get the bytes of the zip file
    zip_buffer.seek(0)

    # Create a Flask response and set the appropriate headers
    response = Response(zip_buffer.read(), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename=reportnet3_dataflow.zip'
    zip_buffer.close()

    return response


@dataflow_endpoint.route('/api/dataflow/showreportnet3', methods=['GET'])
@jwt_required()
def show_reportnet3():
    return jsonify({"showreportnet3": current_app.config['SHOWREPORTNET3']})


@dataflow_endpoint.route('/api/dataflow/reportnet3/b', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_b():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"error": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_dataflowB()
    if not data:
        raise BadRequest("No data for dataflow B found")

    return jsonify(data)


@dataflow_endpoint.route('/api/dataflow/reportnet3/d/processes', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_d_processes():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"error": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_processes()
    if not data:
        raise BadRequest("No data for dataflow D Processes found")

    return jsonify(data)


@dataflow_endpoint.route('/api/dataflow/reportnet3/d/samplingpoints', methods=['GET'])
@jwt_required_with_exporting_claim()
def dataflows_reportnet3_d_samplingpoints():
    if not current_app.config['SHOWREPORTNET3']:
        return jsonify({"error": "Reportnet3 dataflow is not enabled"}), 403

    data = Dataflows_reportnet3.get_samplingpoints()
    if not data:
        raise BadRequest("No data for dataflow D Samplingpoints found")

    return jsonify(data)
