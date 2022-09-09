from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from flask_pydantic import validate
from api.endpoints.management.authorities.models import AuthorityModel, DeleteModel


authorities_endpoint = Blueprint('authorities', __name__)


@authorities_endpoint.route('/api/management/authorities', methods=['GET'])
@jwt_required()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select id, name, organisation, locator, postcode, email, address, phone, website, is_responsible_reporter::varchar 
          from responsible_authorities order by name
        """)
        authorities = cursor.fetchall()
        return jsonify(authorities)


@authorities_endpoint.route('/api/management/authorities/update', methods=['POST'])
@jwt_required()
def authorities_update():
    with CursorFromPool() as cursor:
        model = AuthorityModel(**request.json)
        sql = """            
            UPDATE responsible_authorities
            SET name = %(name)s,
            organisation = %(organisation)s,
            locator = %(locator)s,
            postcode = %(postcode)s,
            email = %(email)s,
            address = %(address)s,
            phone = %(phone)s,
            website = %(website)s,
            is_responsible_reporter = %(is_responsible_reporter)s
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@authorities_endpoint.route('/api/management/authorities/insert', methods=['POST'])
@jwt_required()
def authorities_insert():
    with CursorFromPool() as cursor:
        model = AuthorityModel(**request.json)
        sql = """
            INSERT INTO responsible_authorities (id, name, organisation, locator, postcode, email, address, phone, website, is_responsible_reporter)
            VALUES (%(id)s, %(name)s, %(organisation)s, %(locator)s, %(postcode)s, %(email)s, %(address)s, %(phone)s, %(website)s, %(is_responsible_reporter)s)            
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)
        return jsonify({"success": True})


@authorities_endpoint.route("/api/management/authorities/delete", methods=['POST'])
@jwt_required()
def authorities_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from responsible_authorities where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})
