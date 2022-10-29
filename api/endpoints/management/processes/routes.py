from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.processes.models import ProcessModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_network_claim


processes_endpoint = Blueprint('processes', __name__)


@processes_endpoint.route('/api/management/processes', methods=['GET'])
@jwt_required_with_network_claim()
def processes():
    with CursorFromPool() as cursor:
        cursor.execute("""
        SELECT 
            pr.id,
            pr.measurement_type, 
            pr.measurement_method, 
            pr.other_measurement_method, 
            pr.sampling_method, 
            pr.other_sampling_method, 
            pr.analytical_tech, 
            pr.other_analytical_tech, 
            pr.sampling_equipment, 
            pr.measurement_equipment, 
            pr.equiv_demonstration, 
            pr.equiv_demonstration_report, 
            pr.detection_limit::DOUBLE PRECISION, 
            pr.detection_limit_uom, 
            pr.uncertainty_estimate::DOUBLE PRECISION, 
            pr.documentation, 
            pr.qa_report, 
            pr.duration_number, 
            pr.duration_unit, 
            pr.cadence_number, 
            pr.cadence_unit, 
            pr.responsible_authority_id, 
            pr.other_measurement_equipment, 
            pr.other_sampling_equipment, 
            mt.label as measurement_type_name, 
            mm.label as measurement_method_name, 
            me.label as measurement_equipment_name, 
            tm_d.label as duration_unit_name, 
            tm_c.label as cadence_unit_name, 
            ra.name as responsible_authority,
            ed.label as equiv_demonstration_name,
            ct.notation as detection_limit_uom_name
        FROM 				
				processes pr
            LEFT OUTER JOIN eea_measurementtypes mt ON lower(pr.measurement_type) = lower(mt.id) 
            LEFT OUTER JOIN eea_measurementmethods mm ON lower(pr.measurement_method) = lower(mm.id)
            LEFT OUTER JOIN eea_measurementequipments me ON lower(pr.measurement_equipment) = lower(me.id)
            LEFT OUTER JOIN eea_equivalencedemonstrated ed ON lower(pr.equiv_demonstration) = lower(ed.id)
            LEFT OUTER JOIN responsible_authorities ra ON lower(pr.responsible_authority_id) = lower(ra.id)
            LEFT OUTER JOIN eea_concentrations ct ON lower(pr.detection_limit_uom) = lower(ct.id)
            LEFT OUTER JOIN eea_times tm_d ON lower(pr.duration_unit) = lower(tm_d.id)
            LEFT OUTER JOIN eea_times tm_c ON lower(pr.cadence_unit) = lower(tm_c.id)

        """)
        processes = cursor.fetchall()
        return jsonify(processes)


@processes_endpoint.route('/api/management/processes/update', methods=['POST'])
@jwt_required_with_network_claim()
def processes_update():
    with CursorFromPool() as cursor:
        model = ProcessModel(**request.json)
        sql = """
        INSERT INTO processes (id, measurement_type, measurement_method, other_measurement_method, sampling_method, other_sampling_method, analytical_tech, 
				other_analytical_tech, sampling_equipment, measurement_equipment, equiv_demonstration, equiv_demonstration_report, detection_limit, 
				detection_limit_uom, uncertainty_estimate, documentation, qa_report, duration_number, duration_unit, cadence_number, cadence_unit, 
				responsible_authority_id, other_measurement_equipment, other_sampling_equipment)
            VALUES (%(id)s, %(measurement_type)s, %(measurement_method)s, %(other_measurement_method)s, %(sampling_method)s, %(other_sampling_method)s, %(analytical_tech)s, 
				%(other_analytical_tech)s, %(sampling_equipment)s, %(measurement_equipment)s, %(equiv_demonstration)s, %(equiv_demonstration_report)s, %(detection_limit)s,
				%(detection_limit_uom)s, %(uncertainty_estimate)s, %(documentation)s, %(qa_report)s, %(duration_number)s, %(duration_unit)s, %(cadence_number)s, %(cadence_unit)s, 
				%(responsible_authority_id)s, %(other_measurement_equipment)s, %(other_sampling_equipment)s)
            ON CONFLICT (id) DO 
            UPDATE SET measurement_type=%(measurement_type)s,
				measurement_method=%(measurement_method)s,
				other_measurement_method=%(other_measurement_method)s,
				sampling_method=%(sampling_method)s,
				other_sampling_method=%(other_sampling_method)s,
				analytical_tech=%(analytical_tech)s,
				other_analytical_tech=%(other_analytical_tech)s,
				sampling_equipment=%(sampling_equipment)s,
				measurement_equipment=%(measurement_equipment)s,
				equiv_demonstration=%(equiv_demonstration)s,
				equiv_demonstration_report=%(equiv_demonstration_report)s,
				detection_limit=%(detection_limit)s,
				detection_limit_uom=%(detection_limit_uom)s,
				uncertainty_estimate=%(uncertainty_estimate)s,
				documentation=%(documentation)s,
				qa_report=%(qa_report)s,
				duration_number=%(duration_number)s,
				duration_unit=%(duration_unit)s,
				cadence_number=%(cadence_number)s,
				cadence_unit=%(cadence_unit)s,
				responsible_authority_id=%(responsible_authority_id)s,
				other_measurement_equipment=%(other_measurement_equipment)s,
				other_sampling_equipment=%(other_sampling_equipment)s
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@processes_endpoint.route('/api/management/processes/delete', methods=['POST'])
@jwt_required_with_network_claim()
def processes_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = """
          delete from processes where id = %(id)s  
        """

        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})
