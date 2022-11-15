from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.zones.models import ZoneModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


zones_endpoint = Blueprint('zones', __name__)


@zones_endpoint.route('/api/management/zones', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select z.id, z.code, z.name, z.year, z.area, z.population, z.population_year, z.type as type_id, zt.label as type_label, z.responsible_authority_id as authority_id, r.name as authority_label, ST_AsGeoJSON(geom) as geojson
          from zones z, eea_zonetypes zt, responsible_authorities r
          where z.type = zt.id
          and z.responsible_authority_id = r.id
        """)
        zones = cursor.fetchall()
        return jsonify(zones)


@zones_endpoint.route('/api/management/zones/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_update():
    with CursorFromPool() as cursor:
        model = ZoneModel(**request.json)
        sql = """ 
            UPDATE zones
            SET name = %(name)s,
            year = %(year)s,
            area = %(area)s,
            responsible_authority_id = %(authority_id)s,
            type = %(type_id)s,
            population = %(population)s,
            population_year = %(population_year)s,
            geom = ST_GeomFromGeoJSON(%(geojson)s)
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@zones_endpoint.route('/api/management/zones/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_insert():
    with CursorFromPool() as cursor:
        model = ZoneModel(**request.json)
        sql = """ 
            insert into zones (
                id,
                code,
                name,
                area,
                year,
                responsible_authority_id,                
                type,
                population,
                population_year,
                geom
            )
            values (
                %(id)s,
                %(code)s,
                %(name)s,
                %(area)s,
                %(year)s,
                %(authority_id)s,
                %(type_id)s,
                %(population)s,
                %(population_year)s,
                ST_GeomFromGeoJSON(%(geojson)s)
            ) 
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@zones_endpoint.route("/api/management/zones/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from zones where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})


## LOOKUPS ##

@zones_endpoint.route('/api/management/zones/authorities', methods=['GET'])
@jwt_required_with_management_claim()
def authorities():
    with CursorFromPool() as cursor:
        cursor.execute("select r.name as label, r.id as value from responsible_authorities r order by r.name")
        authorities = cursor.fetchall()
        return jsonify(authorities)


@zones_endpoint.route('/api/management/zones/types', methods=['GET'])
@jwt_required_with_management_claim()
def types():
    with CursorFromPool() as cursor:
        cursor.execute("select r.label as label, r.id as value from eea_zonetypes r order by r.label")
        authorities = cursor.fetchall()
        return jsonify(authorities)
