from flask import jsonify, Blueprint, request
from core.database import CursorFromPool
from endpoints.misc.settings.models import SettingsModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


settings_endpoint = Blueprint('settings', __name__)


@settings_endpoint.route('/api/misc/settings', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def settings():
    with CursorFromPool() as cursor:
        cursor.execute("""
          SELECT s.* 
          FROM settings s   
        """)
        settings = cursor.fetchall()
        return jsonify(settings)


@settings_endpoint.route('/api/misc/settings/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def settings_lookups():
    with CursorFromPool() as cursor:
        cursor.execute("SELECT id as value, label FROM eea_countries ORDER BY LOWER(label)")
        countries = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_timezones ORDER BY LOWER(label)")
        timezones = cursor.fetchall()
        
        return jsonify({
            "countries": countries,
            "timezones": timezones
        })


@settings_endpoint.route('/api/misc/settings/save', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def settings_save():
    with CursorFromPool() as cursor:
        model = SettingsModel(**request.json)
        
        # Delete all existing rows
        cursor.execute("DELETE FROM settings")
        
        # Insert new row
        sql = """
            INSERT INTO settings (country_code_id, timezone_id)
            VALUES (%(country_code_id)s, %(timezone_id)s)
        """
        cursor.execute(sql, model)
        
        return jsonify({"msg": "Settings saved successfully"})
