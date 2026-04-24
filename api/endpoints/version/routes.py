from flask import jsonify, Blueprint, request
from flask_jwt_extended import create_access_token
import requests
import os

version_endpoint = Blueprint('version', __name__)
current_version = os.environ.get("APP_VERSION", "dev")


@version_endpoint.route('/api/version', methods=['GET'])
def version():
    try:
        response = requests.get("https://api.github.com/repos/eea/raven-administration/tags")
        response.raise_for_status()
        j = response.json()
        return {"current": current_version, "latest": j[0]["name"].replace("v.", "")}
    except Exception as err:
        return {"current": current_version, "latest": current_version}
