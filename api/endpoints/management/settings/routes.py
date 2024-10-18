from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query_access import Access
from endpoints.management.settings.models import SettingsModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


settings_endpoint = Blueprint('settings', __name__)


@settings_endpoint.route('/api/management/settings', methods=['GET'])
@jwt_required_with_management_claim()
def settings():
    with CursorFromPool() as cursor:
        cursor.execute("""
          SELECT s.* 
          FROM settings s   
        """)
        settings = cursor.fetchall()
        return jsonify(settings)


@settings_endpoint.route('/api/management/settings/update', methods=['POST'])
@jwt_required_with_management_claim()
def settings_update():
    with CursorFromPool() as cursor:
        model = SettingsModel(**request.json)
        sql = """
            UPDATE settings
            SET
              namespace = %(namespace)s,
              uom_m = %(uom_m)s,
  			      observation_prefix = %(observation_prefix)s,
	      		  language_code = %(language_code)s,
	      		  country = %(country)s,
	      		  country_code = %(country_code)s
            WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
