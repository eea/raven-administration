from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query_access import Access
from endpoints.management.processes.models import ProcessModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


processes_endpoint = Blueprint('processes', __name__)


@processes_endpoint.route('/api/management/processes', methods=['GET'])
@jwt_required_with_management_claim()
def processes():
    with CursorFromPool() as cursor:
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f""" 
          {with_samplingpoints_sql}
          SELECT
              pr.id,
              pr.activity_begin,
              pr.activity_end,
              pr.data_quality_report_id,
              pr.equivalence_demonstration_report_id,
              pr.process_documentation_id,
              pr.measurement_type_id, mt.label as measurement_type,
              pr.method_id, mm.label as method,
              pr.equipment_id, me.label as equipment,
              pr.analytical_technique_id, at.label as analytical_technique,
              pr.equivalence_demonstrated_id, ed.label as equivalence_demonstrated,
              pr.sampling_point_id, sp.id as sampling_point
          FROM processes pr
              LEFT JOIN eea_measurementtypes mt ON pr.measurement_type_id = mt.id
              LEFT JOIN eea_measurementmethods mm ON pr.method_id = mm.id
              LEFT JOIN eea_measurementequipments me ON pr.equipment_id = me.id
              LEFT JOIN eea_analyticaltechnique at ON pr.analytical_technique_id = at.id
              LEFT JOIN eea_equivalencedemonstrated ed ON pr.equivalence_demonstrated_id = ed.id
              INNER JOIN sampling_points sp ON pr.sampling_point_id = sp.id
              INNER JOIN sampling_point_access spa ON sp.id = spa.id
          ORDER BY pr.id
        """, n_param)
        processes = cursor.fetchall()
        return jsonify(processes)


@processes_endpoint.route('/api/management/processes/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def processes_lookups():
    with CursorFromPool() as cursor:
        # Get sampling points accessible to user
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f"""
            {with_samplingpoints_sql}
            SELECT sp.id as value, sp.id as label
            FROM sampling_points sp
            INNER JOIN sampling_point_access spa ON sp.id = spa.id
            ORDER BY sp.id
        """, n_param)
        sampling_points = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_measurementtypes ORDER BY label")
        measurement_types = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_measurementmethods ORDER BY label")
        methods = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_measurementequipments ORDER BY label")
        equipments = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_analyticaltechnique ORDER BY label")
        analytical_techniques = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_equivalencedemonstrated ORDER BY label")
        equivalence_demonstrated = cursor.fetchall()
        
        return jsonify({
            "sampling_points": sampling_points,
            "measurement_types": measurement_types,
            "methods": methods,
            "equipments": equipments,
            "analytical_techniques": analytical_techniques,
            "equivalence_demonstrated": equivalence_demonstrated
        })


@processes_endpoint.route('/api/management/processes/update', methods=['POST'])
@jwt_required_with_management_claim()
def processes_update():
    with CursorFromPool() as cursor:
        model = ProcessModel(**request.json)
        
        if not Access.to_sampling_point(model.sampling_point_id):
            raise BadRequest("Access denied for sampling point")
        
        sql = """        
            UPDATE processes
            SET 
              activity_begin = %(activity_begin)s,
              activity_end = %(activity_end)s,
              data_quality_report_id = %(data_quality_report_id)s,
              equivalence_demonstration_report_id = %(equivalence_demonstration_report_id)s,
              process_documentation_id = %(process_documentation_id)s,
              measurement_type_id = %(measurement_type_id)s,
              method_id = %(method_id)s,
              equipment_id = %(equipment_id)s,
              analytical_technique_id = %(analytical_technique_id)s,
              equivalence_demonstrated_id = %(equivalence_demonstrated_id)s,
              sampling_point_id = %(sampling_point_id)s
            WHERE id = %(id)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"msg": "Process updated successfully"})


@processes_endpoint.route('/api/management/processes/insert', methods=['POST'])
@jwt_required_with_management_claim()
def processes_insert():
    with CursorFromPool() as cursor:
        model = ProcessModel(**request.json)
        
        if not Access.to_sampling_point(model.sampling_point_id):
            raise BadRequest("Access denied for sampling point")
        
        sql = """
          INSERT INTO processes (
            id, activity_begin, activity_end, data_quality_report_id,
            equivalence_demonstration_report_id, process_documentation_id,
            measurement_type_id, method_id, equipment_id,
            analytical_technique_id, equivalence_demonstrated_id, sampling_point_id
          )
          VALUES (
            %(id)s, %(activity_begin)s, %(activity_end)s, %(data_quality_report_id)s,
            %(equivalence_demonstration_report_id)s, %(process_documentation_id)s,
            %(measurement_type_id)s, %(method_id)s, %(equipment_id)s,
            %(analytical_technique_id)s, %(equivalence_demonstrated_id)s, %(sampling_point_id)s
          )            
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"msg": "Process created successfully"})


@processes_endpoint.route('/api/management/processes/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def processes_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("processes", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})

    return jsonify({"msg": "Process deleted successfully"})
