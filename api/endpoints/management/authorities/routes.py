from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query_access import Access
from endpoints.management.authorities.models import AuthorityModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


authorities_endpoint = Blueprint('authorities', __name__)


@authorities_endpoint.route('/api/management/authorities', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("""          
          SELECT a.id, a.person_name, a.email, a.authority_name, a.authority_url, 
                 a.authority_address, 
                 a.authority_instance_id, COALESCE(NULLIF(i.notation, ''), i.label) as authority_instance,
                 a.authority_role_id, COALESCE(NULLIF(o.notation, ''), o.label) as authority_role,
                 a.authority_status_id, COALESCE(NULLIF(s.notation, ''), s.label) as authority_status
          FROM authorities a 
          LEFT JOIN eea_authorityinstance i ON a.authority_instance_id = i.id
          LEFT JOIN eea_authorityobject o ON a.authority_role_id = o.id
          LEFT JOIN eea_authoritystatus s ON a.authority_status_id = s.id
          ORDER BY LOWER(a.authority_name), LOWER(a.person_name)
        """)
        authorities = cursor.fetchall()
        return jsonify(authorities)


@authorities_endpoint.route('/api/management/authorities/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_lookups():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT id as value, label FROM eea_authorityinstance ORDER BY LOWER(label)")
        instances = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_authorityobject ORDER BY LOWER(label)")
        objects = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_authoritystatus ORDER BY LOWER(label)")
        statuses = cursor.fetchall()
        
        return jsonify({
            "instances": instances,
            "objects": objects,
            "statuses": statuses
        })


@authorities_endpoint.route('/api/management/authorities/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_update():
    with CursorFromPool() as cursor:
        model = AuthorityModel(**request.json)
        sql = """            
            UPDATE authorities
            SET person_name = %(person_name)s,
                email = %(email)s,
                authority_name = %(authority_name)s,
                authority_url = %(authority_url)s,
                authority_address = %(authority_address)s,
                authority_instance_id = %(authority_instance_id)s,
                authority_role_id = %(authority_role_id)s,
                authority_status_id = %(authority_status_id)s
            WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"msg": "Authority updated successfully"})


@authorities_endpoint.route('/api/management/authorities/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_insert():
    with CursorFromPool() as cursor:
        model = AuthorityModel(**request.json)
        sql = """
            INSERT INTO authorities (id, person_name, email, authority_name, authority_url, 
                                    authority_address, authority_instance_id, authority_role_id, authority_status_id)
            VALUES (%(id)s, %(person_name)s, %(email)s, %(authority_name)s, %(authority_url)s, 
                    %(authority_address)s, %(authority_instance_id)s, %(authority_role_id)s, %(authority_status_id)s)
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)
        return jsonify({"msg": "Authority created successfully"})


@authorities_endpoint.route("/api/management/authorities/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("authorities", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

    return jsonify({"msg": "Authority deleted successfully"})
