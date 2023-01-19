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
            select n.id, n.name, r.name as authority, r.id as authority_id, v.label as media, v.id as media_id, l.label as organisationlevel, l.id as organisationlevel_id, t.notation as timezone, t.id as timezone_id, n.begin_position, n.end_position
            from networks n, responsible_authorities r, eea_mediavalues v, eea_organisationallevels l, eea_timezones t, network_access na
            where n.responsible_authority_id=r.id
            and n.media_monitored=v.id
            and n.organisational=l.id
            and n.aggregation_timezone=t.id 
            and n.id = na.id
            order by n.name, n.id
        """, n_param)
        authorities = cursor.fetchall()
        return jsonify(authorities)


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
            media_monitored = %(media_id)s,
            organisational = %(organisationlevel_id)s,
            responsible_authority_id = %(authority_id)s,
            aggregation_timezone = %(timezone_id)s,
            begin_position = %(begin_position)s,
            end_position = %(end_position)s
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@networks_endpoint.route('/api/management/networks/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def networks_insert():
    with CursorFromPool() as cursor:
        model = NetworkModel(**request.json)

        sql = """ 
            insert into networks (
                id,
                name,
                media_monitored,
                organisational,                
                responsible_authority_id,
                aggregation_timezone,
                begin_position,
                end_position
            )
            values (
                %(id)s,
                %(name)s,
                %(media_id)s,
                %(organisationlevel_id)s,
                %(authority_id)s,
                %(timezone_id)s,
                %(begin_position)s,
                %(end_position)s
            ) 
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


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

        return jsonify({"success": True})
