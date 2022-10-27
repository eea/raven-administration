from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.core.database import CursorFromPool
from api.core.user import add_user, update_user, remove_user, add_group, update_group, remove_group
from api.endpoints.access.models import InsertModel, UpdateModel, DeleteModel, InsertGroupModel, UpdateGroupModel


access_endpoint = Blueprint('access', __name__)


# USERS
@access_endpoint.route('/api/access/users', methods=['GET'])
@jwt_required()
def users():
    with CursorFromPool() as cursor:
        sql = """
			      select 
              u.id,u.name,u.username,u.createdby, 
              to_char(u.created,'yyyy-mm-dd HH24:mi') as created, 
              array_agg(g.id) as groups, 
              string_agg(g.name,',') as group_labels
            from users u, usergroup ug, "group" g
            where ug.userid = u.id
            and ug.groupid = g.id
            group by u.id,u.name,u.username,u.created
            order by u.id
        """
        cursor.execute(sql)
        values = cursor.fetchall()
        return jsonify(values)


@access_endpoint.route('/api/access/users/insert', methods=['POST'])
@jwt_required()
def users_insert():
    model = InsertModel(**request.json)
    add_user(model.name, model.username, model.password, model.groups, get_jwt_identity())
    return jsonify({"success": True})


@access_endpoint.route('/api/access/users/update', methods=['POST'])
@jwt_required()
def users_update():
    model = UpdateModel(**request.json)
    update_user(model.id, model.name, model.username, model.password, model.groups, get_jwt_identity())
    return jsonify({"success": True})


@access_endpoint.route('/api/access/users/delete', methods=['POST'])
@jwt_required()
def users_delete():
    model = DeleteModel(**request.json)
    remove_user(model.id)
    return jsonify({"success": True})


# GROUPS
@access_endpoint.route('/api/access/groups', methods=['GET'])
@jwt_required()
def groups():
    with CursorFromPool() as cursor:
        sql = """
			      select
                  g.id, g.name, g.network, g.observations, g.exporting, g.processing, g.qualitycontrol, g.allnetworks, g.users,
                  count(ug.groupid) as user_count,
                  coalesce( array_agg(gn.networkid) FILTER (WHERE gn.networkid is not NULL),'{}') as networks
            from
                "group" g
                left join usergroup ug on ug.groupid = g.id
                left join groupnetwork gn on gn.groupid = g.id
            group by g.id, g.name, g.network, g.observations, g.exporting, g.processing, g.qualitycontrol, g.allnetworks, g.users
            order by g.name
        """
        cursor.execute(sql)
        groups = cursor.fetchall()
        return jsonify(groups)


@access_endpoint.route('/api/access/groups/insert', methods=['POST'])
@jwt_required()
def groups_insert():
    model = InsertGroupModel(**request.json)
    add_group(model.name, model.network, model.observations, model.exporting, model.processing, model.qualitycontrol, model.users, model.allnetworks, model.networks)
    return jsonify({"success": True})


@access_endpoint.route('/api/access/groups/update', methods=['POST'])
@jwt_required()
def groups_update():
    model = UpdateGroupModel(**request.json)
    update_group(model.id, model.name, model.network, model.observations, model.exporting, model.processing, model.qualitycontrol, model.users, model.allnetworks, model.networks)
    return jsonify({"success": True})


@access_endpoint.route('/api/access/groups/delete', methods=['POST'])
@jwt_required()
def groups_delete():
    model = DeleteModel(**request.json)
    remove_group(model.id)
    return jsonify({"success": True})


# LOOKUPS
@access_endpoint.route('/api/access/networks', methods=['GET'])
@jwt_required()
def networks():
    with CursorFromPool() as cursor:
        sql = """
            select id as value, name as label
            from networks
            order by name
        """
        cursor.execute(sql)
        networks = cursor.fetchall()
        return jsonify(networks)
