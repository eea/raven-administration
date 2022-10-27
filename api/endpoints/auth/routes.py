from flask import jsonify, Blueprint, request
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest
from api.core.user import get_user

auth_endpoint = Blueprint('auth', __name__)


@auth_endpoint.route('/api/auth/signin', methods=['POST'])
def login():
    usr = request.json["username"]
    pwd = request.json["password"]
    if usr and pwd:
        user = get_user(usr, pwd)
        if user != None:
            token = create_access_token(identity=user.username)
            return jsonify({"token": token})
        else:
            raise BadRequest("Incorrect username or password")
    else:
        raise BadRequest("Username or password not found")
