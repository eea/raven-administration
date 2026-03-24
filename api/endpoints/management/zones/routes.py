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
          select 
            z.id, 
            z.code, 
            z.name, 
            z.area, 
            z.zone_type_id, 
            zt.notation as zone_type,
            z.zone_category_id,
            COALESCE(NULLIF(zc.notation, ''), zc.label) as zone_category,
            ST_AsGeoJSON(z.geom) as geojson          
          from zones z
          left join eea_zonetypes zt on z.zone_type_id = zt.id
          left join eea_zonecategory zc on z.zone_category_id = zc.id
        """)
        zones = cursor.fetchall()
        return jsonify(zones)


@zones_endpoint.route('/api/management/zones/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_update():
    with CursorFromPool() as cursor:
        model = ZoneModel(**request.json)
        
        # If source EPSG is 4326, use directly; otherwise transform to 4326
        if model.source_epsg == 4326:
            geom_sql = "ST_SetSRID(ST_GeomFromGeoJSON(%(geojson)s), 4326)"
        else:
            geom_sql = f"ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%(geojson)s), %(source_epsg)s), 4326)"
        
        sql = f""" 
            UPDATE zones
            SET 
                code = %(code)s,
                name = %(name)s,
                area = %(area)s,
                zone_type_id = %(zone_type_id)s,
                zone_category_id = %(zone_category_id)s,
                geom = {geom_sql}
            where id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@zones_endpoint.route('/api/management/zones/add', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def zones_add():
    with CursorFromPool() as cursor:
        model = ZoneModel(**request.json)
        
        # If source EPSG is 4326, use directly; otherwise transform to 4326
        if model.source_epsg == 4326:
            geom_sql = "ST_SetSRID(ST_GeomFromGeoJSON(%(geojson)s), 4326)"
        else:
            geom_sql = f"ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%(geojson)s), %(source_epsg)s), 4326)"
        
        sql = f"""
            INSERT INTO zones (id, code, name, area, zone_type_id, zone_category_id, geom)
            VALUES (%(id)s, %(code)s, %(name)s, %(area)s, %(zone_type_id)s, %(zone_category_id)s, 
                    {geom_sql})
        """
        cursor.execute(sql, model)
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
