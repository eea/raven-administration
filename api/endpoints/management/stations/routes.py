from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.stations.models import StationModel
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query_access import Access
from core.query import Q, DeleteModel

stations_endpoint = Blueprint('stations', __name__)


@stations_endpoint.route('/api/management/stations', methods=['GET'])
@jwt_required_with_management_claim()
def stations():
    with CursorFromPool() as cursor:
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
          {with_network_sql} 
          SELECT st.id, st.eoi_code, st.name, st.national_code,
                 st.latitude, st.longitude, st.altitude, st.supersite,
                 st.area_classification_id, ac.label as area_classification,
                 st.network_id, n.name as network,
                 st.document_id, d.id || ' - ' || COALESCE(dobj.label, '') as document
          FROM stations st
          LEFT JOIN eea_areaclassifications ac ON st.area_classification_id = ac.id
          INNER JOIN networks n ON st.network_id = n.id
          INNER JOIN network_access na ON n.id = na.id
          LEFT JOIN documents d ON st.document_id = d.id
          LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
          ORDER BY st.name, st.id
        """, n_param)
        stations = cursor.fetchall()
        return jsonify(stations)


@stations_endpoint.route('/api/management/stations/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def stations_lookups():
    with CursorFromPool() as cursor:
        # Get networks accessible to user
        with_network_sql, n_param = Q.with_networks_by_access_as_sql()
        cursor.execute(f"""
            {with_network_sql}
            SELECT n.id as value, n.name as label
            FROM networks n, network_access na
            WHERE n.id = na.id
            ORDER BY n.name
        """, n_param)
        networks = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_areaclassifications ORDER BY label")
        areaclassifications = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_spocategory ORDER BY label")
        spocategories = cursor.fetchall()
        
        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'station'
            ORDER BY d.id
        """)
        documents = cursor.fetchall()
        
        return jsonify({
            "networks": networks,
            "areaclassifications": areaclassifications,
            "spocategories": spocategories,
            "documents": documents
        })


@stations_endpoint.route('/api/management/stations/update', methods=['POST'])
@jwt_required_with_management_claim()
def stations_update():
    with CursorFromPool() as cursor:
        model = StationModel(**request.json)

        if not Access.to_station(model.id):
            raise BadRequest("Access denied for station")

        sql = """ 
            UPDATE stations
            SET eoi_code = %(eoi_code)s,
                name = %(name)s,
                national_code = %(national_code)s,
                latitude = %(latitude)s,
                longitude = %(longitude)s,
                altitude = %(altitude)s,
                supersite = %(supersite)s,
                area_classification_id = %(area_classification_id)s,
                network_id = %(network_id)s,
                document_id = %(document_id)s
            WHERE id = %(id)s
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"msg": "Station updated successfully"})


@stations_endpoint.route('/api/management/stations/insert', methods=['POST'])
@jwt_required_with_management_claim()
def stations_insert():
    with CursorFromPool() as cursor:
        model = StationModel(**request.json)

        if not Access.to_network(model.network_id):
            raise BadRequest("Access denied for network")

        sql = """ 
            INSERT INTO stations (id, eoi_code, name, national_code, latitude, longitude, 
                                 altitude, supersite, area_classification_id, network_id, document_id)
            VALUES (%(id)s, %(eoi_code)s, %(name)s, %(national_code)s, %(latitude)s, %(longitude)s,
                   %(altitude)s, %(supersite)s, %(area_classification_id)s, %(network_id)s, %(document_id)s)
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"msg": "Station created successfully"})


@stations_endpoint.route("/api/management/stations/delete", methods=['POST'])
@jwt_required_with_management_claim()
def stations_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)

        if not Access.to_stations(model.ids):
            raise BadRequest("Access denied for stations")

        rows = Q.delete("stations", model)
        if rows == 0:
            raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

        return jsonify({"msg": "Station deleted successfully"})
