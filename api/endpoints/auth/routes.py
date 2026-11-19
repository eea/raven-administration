from flask import jsonify, Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from core.database import CursorFromPool
from werkzeug.exceptions import BadRequest
from core.user import get_user, get_user_by_username, get_claims, add_admin, are_user_and_group_table_empty
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

auth_endpoint = Blueprint('auth', __name__)


@auth_endpoint.route('/api/auth/signin', methods=['POST'])
def login():
    usr = request.json["username"]
    pwd = request.json["password"]
    if usr and pwd:
        user = get_user(usr, pwd)
        if user != None:
            token = create_access_token(identity=user.username, additional_claims=get_claims(user))
            return jsonify({"token": token})
        else:
            raise BadRequest("Incorrect username or password")
    else:
        raise BadRequest("Username or password not found")


@auth_endpoint.route('/api/auth/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Re-issue the token before it expires ("Stay signed in").

    Needs a still-valid token, so an expired session still means a password login.
    Claims are re-read, so group changes made meanwhile take effect.
    """
    user = get_user_by_username(get_jwt_identity())
    if user is None:
        return jsonify(msg="User no longer exists"), 401
    token = create_access_token(identity=user.username, additional_claims=get_claims(user))
    return jsonify({"token": token})


@auth_endpoint.route('/api/auth/cancreateadmin', methods=['GET'])
def cancreateadmin():
    return jsonify({"cancreateadmin": are_user_and_group_table_empty()})


@auth_endpoint.route('/api/auth/create', methods=['POST'])
def create():
    add_admin(request.json["password"])
    return jsonify({"success": True})
