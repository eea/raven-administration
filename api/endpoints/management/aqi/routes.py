from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core.query import Q
aqi_endpoint = Blueprint('aqi', __name__)


@aqi_endpoint.route('/api/management/aqi', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def aqi():
    with CursorFromPool() as cursor:
        sql = """
            select p.notation as pollutant,t.label as timestep, i.level, i.description, i.color, lower(i.range) as range_from, upper(i.range) as range_to, p.uri as pollutant_uri, t.id as timestep_uri
            from aqi_test i, eea_pollutants p, eea_times t
            where i.pollutant_uri = p.uri
            and i.timestep = t.id
            and i.calculation_type = 'LOCAL'
            order by pollutant, timestep, level
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@aqi_endpoint.route('/api/management/aqi/save', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def save_aqi():
    data = request.json

    # delete existing entries in aqi_test
    # add new entries from data
    with CursorFromPool() as cursor:
        cursor.execute("DELETE FROM aqi_test WHERE calculation_type = 'LOCAL'")

        for item in data:
            sql = """
              INSERT INTO aqi_test (pollutant_uri, timestep, level, range, description, color, calculation_type)
              VALUES (%s, %s, %s, numrange(%s, %s, '[]'), %s, %s, 'LOCAL')
            """
            cursor.execute(sql, (
                item['pollutant_uri'],
                item['timestep_uri'],
                item['level'],
                item['range_from'],
                item['range_to'],
                item['description'],
                item['color']
            ))
        return jsonify({"success": True})
