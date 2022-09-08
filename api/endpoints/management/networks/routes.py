from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.networks.models import NetworkModel, DeleteModel
from api.core.query import Q


networks_endpoint = Blueprint('networks', __name__)


@networks_endpoint.route('/api/management/networks', methods=['GET'])
@jwt_required()
def networks():
    with CursorFromPool() as cursor:
        cursor.execute("""
            select n.id, n.name, r.name as authority, r.id as authority_id, v.label as media, v.id as media_id, l.label as organisationlevel, l.id as organisationlevel_id, t.notation as timezone, t.id as timezone_id, n.begin_position, n.end_position
            from networks n, responsible_authorities r, eea_mediavalues v, eea_organisationallevels l, eea_timezones t
            where n.responsible_authority_id=r.id
            and n.media_monitored=v.id
            and n.organisational=l.id
            and n.aggregation_timezone=t.id
            order by n.name, n.id
        """)
        authorities = cursor.fetchall()
        return jsonify(authorities)


@networks_endpoint.route('/api/management/networks/update', methods=['POST'])
@jwt_required()
def networks_update():
    with CursorFromPool() as cursor:
        model = NetworkModel(**request.json)
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
@jwt_required()
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
@jwt_required()
def networks_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from networks where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##

@networks_endpoint.route('/api/management/networks/authorities', methods=['GET'])
@jwt_required()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@networks_endpoint.route('/api/management/networks/levels', methods=['GET'])
@jwt_required()
def levels():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_organisationallevels r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@networks_endpoint.route('/api/management/networks/media', methods=['GET'])
@jwt_required()
def media():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_mediavalues r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@networks_endpoint.route('/api/management/networks/timezones', methods=['GET'])
@jwt_required()
def timezones():
    timezones = Q.timezones()
    return jsonify(timezones)
