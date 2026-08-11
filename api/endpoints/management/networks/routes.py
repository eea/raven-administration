from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.networks.models import NetworkModel
from core.query import Q, DeleteModel
from core.query_access import Access
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


networks_endpoint = Blueprint('networks', __name__)


@networks_endpoint.route('/api/management/networks', methods=['GET'])
@jwt_required_with_management_claim()
def networks():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""            
            {with_network_sql}
            SELECT n.id, n.name,
                   n.network_organisational_level_id, COALESCE(NULLIF(a.notation, ''), a.label) as network_organisational_level,
                   n.timezone_id, COALESCE(NULLIF(tz.notation, ''), tz.label) as timezone,
                   n.network_document_id, d.id || ' - ' || COALESCE(dobj.label, '') as network_document
            FROM networks n
            LEFT JOIN eea_administrativelevels a ON n.network_organisational_level_id = a.id
            LEFT JOIN eea_timezones tz ON n.timezone_id = tz.id
            LEFT JOIN documents d ON n.network_document_id = d.id
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            INNER JOIN network_access na ON n.id = na.id
            ORDER BY LOWER(n.name), n.id
        """, n_param)
        networks = cursor.fetchall()
        return jsonify(networks)


@networks_endpoint.route('/api/management/networks/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def networks_lookups():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT id as value, label FROM eea_administrativelevels ORDER BY LOWER(label)")
        levels = cursor.fetchall()

        cursor.execute("SELECT id as value, COALESCE(NULLIF(notation, ''), label) as label FROM eea_timezones ORDER BY COALESCE(NULLIF(notation, ''), label)")
        timezones = cursor.fetchall()

        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'network'
            ORDER BY d.id
        """)
        network_documents = cursor.fetchall()

        return jsonify({
            "levels": levels,
            "timezones": timezones,
            "network_documents": network_documents
        })


@networks_endpoint.route('/api/management/networks/update', methods=['POST'])
@jwt_required_with_management_claim()
def networks_update():
    with CursorFromPool() as cursor:
        model = NetworkModel(**request.json)

        if not Access.to_network(model.id):
            raise BadRequest("Access denied for network")

        sql = """ 
            UPDATE networks
            SET name = %(name)s,
                network_organisational_level_id = %(network_organisational_level_id)s,
                timezone_id = %(timezone_id)s,
                network_document_id = %(network_document_id)s
            WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"msg": "Network updated successfully"})


@networks_endpoint.route('/api/management/networks/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def networks_insert():
    with CursorFromPool() as cursor:
        model = NetworkModel(**request.json)

        sql = """ 
            INSERT INTO networks (id, name, network_organisational_level_id, timezone_id, network_document_id)
            VALUES (%(id)s, %(name)s, %(network_organisational_level_id)s, %(timezone_id)s, %(network_document_id)s)
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"msg": "Network created successfully"})


@networks_endpoint.route("/api/management/networks/delete", methods=['POST'])
@jwt_required_with_management_claim()
def networks_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if not Access.to_networks(model.ids):
            raise BadRequest("Access denied for network")

        rows = Q.delete("networks", model)
        if rows == 0:
            raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

        return jsonify({"msg": "Network deleted successfully"})
