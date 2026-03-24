from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.exceedances.models import ExceedanceModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim

exceedances_endpoint = Blueprint('management_exceedances', __name__)

@exceedances_endpoint.route('/api/management/exceedances', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances():
    with CursorFromPool() as cursor:
        cursor.execute("""
            WITH data as (
              SELECT ed.id as exceedance_description_id
              FROM
                assessmentdata ad,
                assessment_regimes ar,
                attainments at,
                exceedancedescriptions ed
              WHERE 1=1
              AND ad.assessment_regime_id = ar.id
              AND ar.id = at.assessment_regime_id
              AND at.id = ed.attainment_id
          )
          SELECT
              count(m.exceedance_description_id) spo_count,
              ed.id,
              ed.exceedances as has_exceedance,
              ed.max_value as exceedance_value,
              ed.surface_area,
              ed.exposed_population,
              ed.population_reference_year as population_year,
              ed.vegetation_area,
              ed.other_exceedance_reason as other_reason,
              a.id as attainment_id,
              a.name as attainment,
              et.id::varchar as exceedance_type_id,
              COALESCE(NULLIF(et.notation, ''), et.label) as exceedance_type,
              ee.id::varchar as exceedance_description_id,
              COALESCE(NULLIF(ee.notation, ''), ee.label) as exceedance_description,
              ed.adjustment_type as adjustment_type_id,
              COALESCE(NULLIF(at.notation, ''), at.label) as adjustment_type,
              ed.area_classification as area_classification_id,
              ac.notation as area_classification,
              ed.exceedance_reason as reason_id,
              COALESCE(NULLIF(er.notation, ''), er.label) as reason,
              ed.adjustment_source as adjustment_source_id,
              COALESCE(NULLIF(es.notation, ''), es.label) as adjustment_source
          FROM
              attainments a,
              eea_exceedancetype et,
              eea_exceedancedescription ee,
              exceedancedescriptions ed
                LEFT OUTER JOIN data m ON ed.id = m.exceedance_description_id
                LEFT OUTER JOIN eea_adjustmentsourcetype es ON ed.adjustment_source = es.id
                LEFT OUTER JOIN eea_adjustmenttypes at ON ed.adjustment_type = at.id
                LEFT OUTER JOIN eea_areaclassifications ac ON ed.area_classification = ac.id
                LEFT OUTER JOIN eea_exceedancereason er ON ed.exceedance_reason = er.id
          WHERE 1=1
          AND ed.attainment_id =  a.id
          AND ed.excedance_type =  et.id
          AND ed.exceedancedescription_element = ee.id
          GROUP BY
              ed.id,
              ed.exceedances,
              ed.max_value,
              ed.surface_area,
              ed.exposed_population,
              ed.population_reference_year,
              ed.vegetation_area,
              ed.other_exceedance_reason,
              a.id ,
              a.name,
              et.id::varchar,
              et.label,
              ee.id::varchar,
              ee.label,
              ed.adjustment_type,
              at.label ,
              ed.area_classification,
              ac.notation,
              ed.exceedance_reason,
              er.label,
              ed.adjustment_source,
              es.label
          ORDER BY a.name
        """)

        exceedances = cursor.fetchall()
        return jsonify(exceedances)


@exceedances_endpoint.route('/api/management/exceedances/samplingpoints', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select
              at.id as attainment_id,
              s.name as station,
              sp.id as sampling_point_id,
              po.notation as pollutant,
              COALESCE(NULLIF(t.notation, ''), t.label) as timestep,
              u.notation as concentration,
              ar.id as assessment_regime
          from
              stations s,
              eea_pollutants po,
              sampling_points sp,
              eea_concentrations u,
              eea_times t,
              assessmentdata ad,
              assessment_regimes ar,
              attainments at
          where 1=1
          and sp.station_id = s.id
          and sp.pollutant_id = po.id
          and sp.time_resolution_id = t.id
          and sp.unit_id = u.id
          and sp.id = ad.assessmentlocal_id
          and ad.assessment_regime_id = ar.id
          and at.assessment_regime_id = ar.id
          order by ar.id, s.name, po.notation, t.label
        """)

        samplingpoints = cursor.fetchall()
        return jsonify(samplingpoints)


@exceedances_endpoint.route('/api/management/exceedances/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances_update():
    with CursorFromPool() as cursor:
        model = ExceedanceModel(**request.json)

        # Update
        sql_update = """            
          UPDATE exceedancedescriptions
          SET 
            attainment_id = %(attainment_id)s,
            exceedances = %(has_exceedance)s,
            excedance_type = %(exceedance_type_id)s,
            max_value = %(exceedance_value)s,
            adjustment_type = %(adjustment_type_id)s,
            surface_area = %(surface_area)s,
            exposed_population = %(exposed_population)s,
            population_reference_year = %(population_year)s,
            vegetation_area = %(vegetation_area)s,
            area_classification = %(area_classification_id)s,
            exceedance_reason = %(reason_id)s,
            other_exceedance_reason = %(other_reason)s,
            exceedancedescription_element = %(exceedance_description_id)s,
            adjustment_source = %(adjustment_source_id)s
          WHERE id = %(id)s
        """
        cursor.execute(sql_update, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@exceedances_endpoint.route('/api/management/exceedances/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances_insert():
    with CursorFromPool() as cursor:
        model = ExceedanceModel(**request.json)
        sql = """
            INSERT INTO exceedancedescriptions (
              id, 
              attainment_id, 
              exceedances, 
              excedance_type, 
              max_value, 
              adjustment_type, 
              surface_area, 
              exposed_population, 
              population_reference_year, 
              vegetation_area, 
              area_classification,
              exceedance_reason, 
              other_exceedance_reason, 
              exceedancedescription_element,
              adjustment_source
            )
            VALUES (
                %(id)s, 
                %(attainment_id)s, 
                %(has_exceedance)s, 
                %(exceedance_type_id)s, 
                %(exceedance_value)s,
                %(adjustment_type_id)s,
                %(surface_area)s, 
                %(exposed_population)s,
                %(population_year)s,
                %(vegetation_area)s,
                %(area_classification_id)s,
                %(reason_id)s,
                %(other_reason)s,
                %(exceedance_description_id)s,                
                %(adjustment_source_id)s
            )             
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        return jsonify({"success": True})


@exceedances_endpoint.route("/api/management/exceedances/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("exceedancedescriptions", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})
    return jsonify({"success": True})
