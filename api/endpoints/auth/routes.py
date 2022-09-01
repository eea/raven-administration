from flask import jsonify, Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest


auth_endpoint = Blueprint('auth', __name__)


@auth_endpoint.route('/api/auth/signin', methods=['POST'])
def login():
    usr = request.json["username"]
    pwd = request.json["password"]
    if usr and pwd:
        if usr == "cst" and pwd == "cst":
            token = create_access_token(identity="cst")
            return jsonify({"token": token})
        else:
            raise BadRequest("Incorrect username or password")
    else:
        raise BadRequest("Username or password not found")
