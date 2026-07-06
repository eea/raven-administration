import json
from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from psycopg2 import errors
from core.database import CursorFromPool
from endpoints.data.favorites.models import FavoriteInsertModel, FavoriteUpdateModel, FavoriteDeleteModel

favorites_endpoint = Blueprint('favorites', __name__)

# Per-user named favorites (dashboard plot configs). Every statement is scoped
# to the current JWT user, so users can only ever see/modify their own rows.
# Plain jwt_required: favorites are used across data and qualitycontrol views.


@favorites_endpoint.route('/api/data/favorites', methods=['GET'])
@jwt_required()
def favorites():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT f.id, f.name, f.config,
                   to_char(f.created, 'YYYY-MM-DD HH24:MI') AS created,
                   to_char(f.updated, 'YYYY-MM-DD HH24:MI') AS updated
            FROM user_favorites f
            JOIN users u ON u.id = f.user_id
            WHERE u.username = %(username)s
            ORDER BY LOWER(f.name)
        """, {"username": get_jwt_identity()})
        return jsonify(cursor.fetchall())


@favorites_endpoint.route('/api/data/favorites/insert', methods=['POST'])
@jwt_required()
def favorites_insert():
    model = FavoriteInsertModel(**request.json)
    try:
        with CursorFromPool() as cursor:
            cursor.execute("""
                INSERT INTO user_favorites (user_id, name, config)
                VALUES ((SELECT id FROM users WHERE username = %(username)s), %(name)s, %(config)s)
            """, {"username": get_jwt_identity(), "name": model.name, "config": json.dumps(model.config)})
    except errors.UniqueViolation:
        return jsonify({"msg": f"A favorite named '{model.name}' already exists"}), 400
    return jsonify({"msg": "Favorite saved successfully"})


@favorites_endpoint.route('/api/data/favorites/update', methods=['POST'])
@jwt_required()
def favorites_update():
    model = FavoriteUpdateModel(**request.json)
    try:
        with CursorFromPool() as cursor:
            cursor.execute("""
                UPDATE user_favorites f
                SET name = %(name)s, config = %(config)s, updated = now()
                FROM users u
                WHERE u.id = f.user_id AND u.username = %(username)s AND f.id = %(id)s
            """, {"username": get_jwt_identity(), "id": model.id, "name": model.name, "config": json.dumps(model.config)})
    except errors.UniqueViolation:
        return jsonify({"msg": f"A favorite named '{model.name}' already exists"}), 400
    return jsonify({"msg": "Favorite updated successfully"})


@favorites_endpoint.route('/api/data/favorites/delete', methods=['POST'])
@jwt_required()
def favorites_delete():
    model = FavoriteDeleteModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM user_favorites f
            USING users u
            WHERE u.id = f.user_id AND u.username = %(username)s AND f.id = %(id)s
        """, {"username": get_jwt_identity(), "id": model.id})
    return jsonify({"msg": "Favorite deleted successfully"})
