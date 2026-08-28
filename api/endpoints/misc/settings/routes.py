import json

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
    """Save the settings singleton, touching only the fields the request supplies.

    This used to be DELETE-then-INSERT with a literal column list, which made every
    save a full replacement: any column missing from that list was silently blanked,
    and pydantic's default extra='ignore' meant a field missing from SettingsModel was
    dropped without a word. Adding observation_log_config under that scheme would have
    meant a rule set quietly wiped the next time somebody changed the timezone.

    So the write is now an UPDATE of the present fields, with an INSERT only when the
    row does not exist yet. Absent means "leave alone"; present means "replace",
    including with an empty value. Nothing outside the request body is touched.
    """
    with CursorFromPool() as cursor:
        model = SettingsModel(**request.json)
        supplied = model.model_fields_set

        params = {
            "country_code_id": model.country_code_id,
            "timezone_id": model.timezone_id,
            # psycopg2 will not adapt a bare dict to jsonb, hence the dumps.
            "observation_log_config": json.dumps(model.observation_log_config or {}),
        }

        assignments = ["country_code_id = %(country_code_id)s",
                       "timezone_id = %(timezone_id)s"]
        if 'observation_log_config' in supplied:
            assignments.append("observation_log_config = %(observation_log_config)s")

        cursor.execute(f"UPDATE settings SET {', '.join(assignments)}", params)

        if cursor.rowcount == 0:
            cursor.execute("""
                INSERT INTO settings (country_code_id, timezone_id, observation_log_config)
                VALUES (%(country_code_id)s, %(timezone_id)s, %(observation_log_config)s)
            """, params)

        return jsonify({"msg": "Settings saved successfully"})
