from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.query import Q, DeleteModel
from core.database import CursorFromPool
from endpoints.management.zones.models import ZoneModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


zones_endpoint = Blueprint('zones', __name__)


@zones_endpoint.route('/api/management/zones', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select z.id, z.code, z.name, z.year, z.area, z.population, z.population_year, z.type as zone_type_id, zt.label as zone_type, z.responsible_authority_id as authority_id, r.name as authority, ST_AsGeoJSON(geom) as geojson          
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
            type = %(zone_type_id)s,
            population = %(population)s,
            population_year = %(population_year)s 
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@zones_endpoint.route("/api/management/zones/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("zones", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

    return jsonify({"success": True})
