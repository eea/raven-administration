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
            SELECT n.id, n.name, n.report_id,
                   n.administration_level_id, a.label as administration_level
            FROM networks n
            LEFT JOIN eea_administrativelevels a ON n.administration_level_id = a.id
            INNER JOIN network_access na ON n.id = na.id
            ORDER BY n.name, n.id
        """, n_param)
        networks = cursor.fetchall()
        return jsonify(networks)


@networks_endpoint.route('/api/management/networks/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def networks_lookups():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT id as value, label FROM eea_administrativelevels ORDER BY label")
        levels = cursor.fetchall()
        
        return jsonify({
            "levels": levels
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
                report_id = %(report_id)s,
                administration_level_id = %(administration_level_id)s
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
            INSERT INTO networks (id, name, report_id, administration_level_id)
            VALUES (%(id)s, %(name)s, %(report_id)s, %(administration_level_id)s)
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
