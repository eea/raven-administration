"""AQR3 AUT Authority CRUD.

Composite primary key (id, authority_role_id, email) — the AQR3 key minus
CountryCode, which is instance-wide — so this does not use the generic Manager
delete: `Q.delete`'s `where id in (...)` cannot address it, and an UPDATE keyed on
`id` alone would rewrite every authority sharing that instance. One instance is
meant to carry several: a country reports its reporting authority and, separately,
its national reference laboratory.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                 jwt_required_with_management_claim)

from .models import AuthorityKey, AuthorityModel

authorities_endpoint = Blueprint('authorities', __name__)

BASE = '/api/management/authorities'

KEY = ('id', 'authority_role_id', 'email')
VALUES = ('person_name', 'authority_name', 'authority_url', 'authority_address',
          'authority_instance_id', 'authority_status_id')


@authorities_endpoint.route(BASE, methods=['GET'])
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
          ORDER BY a.id, a.authority_role_id, a.email
        """)
        return jsonify(cursor.fetchall())


@authorities_endpoint.route(f'{BASE}/lookups', methods=['GET'])
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


@authorities_endpoint.route(f'{BASE}/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_update():
    """Update one authority, identified by `key`, with the values in `values`.

    All three key parts are editable, so the key travels separately: the SET clause
    writes the new key while the WHERE clause still matches the old one.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest("Body must be {key: {id, authority_role_id, email}, "
                         "values: {...}}")

    key = AuthorityKey(**body['key'])
    model = AuthorityModel(**body['values'])

    assignments = ', '.join([f'{c} = %(new_{c})s' for c in KEY] +
                            [f'{c} = %({c})s' for c in VALUES])
    params = {c: model[c] for c in VALUES}
    params.update({f'new_{c}': model[c] for c in KEY})
    params.update({c: key[c] for c in KEY})

    with CursorFromPool() as cursor:
        cursor.execute(f"""
            UPDATE authorities
            SET {assignments}
            WHERE id = %(id)s
              AND authority_role_id = %(authority_role_id)s
              AND email = %(email)s
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(f'No authority for {key.id} / {key.authority_role_id} / '
                             f'{key.email}')

    return jsonify({"msg": "Authority updated successfully"})


@authorities_endpoint.route(f'{BASE}/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_insert():
    model = AuthorityModel(**(request.json or {}))
    columns = KEY + VALUES
    with CursorFromPool() as cursor:
        cursor.execute(f"""
            INSERT INTO authorities ({', '.join(columns)})
            VALUES ({', '.join(f'%({c})s' for c in columns)})
        """, model)
    return jsonify({"msg": "Authority created successfully"}), 201


@authorities_endpoint.route(f'{BASE}/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def authorities_delete():
    key = AuthorityKey(**(request.json or {}))
    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM authorities
            WHERE id = %(id)s
              AND authority_role_id = %(authority_role_id)s
              AND email = %(email)s
        """, key)
        if cursor.rowcount == 0:
            raise BadRequest(f'No authority for {key.id} / {key.authority_role_id} / '
                             f'{key.email}')

    return jsonify({"msg": "Authority deleted successfully"})
