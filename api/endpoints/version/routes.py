from flask import jsonify, Blueprint, request
from flask_jwt_extended import create_access_token
import requests

version_endpoint = Blueprint('version', __name__)
current_version = "3.1.0"


@version_endpoint.route('/api/version', methods=['GET'])
def version():
    try:
        response = requests.get("https://git.nilu.no/api/v4/projects/983/repository/tags")
        response.raise_for_status()
        j = response.json()
        return {"current": current_version, "latest": j[0]["name"].replace("v.", "")}
    except Exception as err:
        return {"current": current_version, "latest": current_version}
