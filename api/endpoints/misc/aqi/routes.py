from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core.query import Q
aqi_endpoint = Blueprint('aqi', __name__)


@aqi_endpoint.route('/api/misc/aqi', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def aqi():
    with CursorFromPool() as cursor:
        sql = """
            select 
                COALESCE(NULLIF(p.notation, ''), p.label) as pollutant,
                t.label as timestep, 
                i.level, 
                i.description, 
                i.color, 
                lower(i.range) as range_from, 
                upper(i.range) as range_to, 
                p.id as pollutant_id, 
                t.id as timestep_id
            from aqi i
            join eea_pollutants p on i.pollutant_id = p.id
            join eea_times t on i.timestep = t.id
            where i.calculation_type = 'LOCAL'
            order by pollutant, timestep, level
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@aqi_endpoint.route('/api/misc/aqi/save', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def save_aqi():
    data = request.json

    # delete existing entries in aqi
    # add new entries from data
    with CursorFromPool() as cursor:
        cursor.execute("DELETE FROM aqi WHERE calculation_type = 'LOCAL'")

        for item in data:
            sql = """
              INSERT INTO aqi (pollutant_id, timestep, level, range, description, color, calculation_type)
              VALUES (%s, %s, %s, numrange(%s, %s, '[]'), %s, %s, 'LOCAL')
            """
            cursor.execute(sql, (
                item['pollutant_id'],
                item['timestep_id'],
                item['level'],
                item['range_from'],
                item['range_to'],
                item['description'],
                item['color']
            ))
        return jsonify({"msg": "AQI configuration saved successfully"})
