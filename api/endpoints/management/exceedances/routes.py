from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.exceedances.models import ExceedanceModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


exceedances_endpoint = Blueprint('exceedances', __name__)


@exceedances_endpoint.route('/api/management/exceedances', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances():
    with CursorFromPool() as cursor:
        cursor.execute("""
          WITH data as (
              SELECT
                true as selected,
                m.id,
                m.assessmentdata_id as assessment_data_id,
                m.exceedancedescription_id as exceedance_description_id,
                s.name as station,
                po.notation as pollutant,
                t.label as timestep,
                u.notation as concentration,
                ar.name as assessment_regime
              FROM
                stations s,
                eea_pollutants po,
                sampling_points sp,
                eea_concentrations u,
                eea_times t,
                exceedingmethods m,
                assessmentdata ad,
                assessmentregimes ar
              WHERE 1=1
              AND sp.station_id = s.id
              AND sp.pollutant = po.uri
              AND sp.timestep = t.id
              AND sp.concentration = u.id
              AND sp.id = ad.assessmentlocal_id
              AND ad.id = m.assessmentdata_id
              AND ad.assessmentregime_id = ar.id
          )
          SELECT
              case when count(m.id) = 0 then '[]' else json_agg(m) end as data,
              count(m.id) spo_count,
              ed.id,
              ed.exceedances as has_exceedance,
              ed.max_value as exceedance_value,
              ed.surface_area,
              ed.exposed_population,
              ed.population_reference_year as population_year,
              ed.vegetation_area,
              ed.other_exceedance_reason as other_reason,
              ed.modelassessmentmetadata as model_assessment_metadata,


              a.id as attainment_id,
              a.name as attainment,
              et.id::varchar as exceedance_type_id,
              et.name as exceedance_type,
              ee.id::varchar as exceedance_description_id,
              ee.name as exceedance_description,
              ed.adjustment_type as adjustment_type_id,
              at.label as adjustment_type,
              ed.area_classification as area_classification_id,
              ac.notation as area_classification,
              ed.exceedance_reason as reason_id,
              er.label as reason,
              ed.adjustment_source as adjustment_source_id,
              es.label as adjustment_source
          FROM
              attainments a,
              eea_exceedancetype et,
              eea_exceedancedescription ee,
              eea_adjustmenttypes at,
              eea_areaclassifications ac,
              eea_exceedancereason er,
              exceedancedescriptions ed
                LEFT OUTER JOIN data m ON ed.id = m.exceedance_description_id
                LEFT OUTER JOIN eea_adjustmentsourcetype es ON ed.adjustment_source = es.id
          WHERE 1=1
          AND ed.attainment_id =  a.id
          AND ed.excedance_type =  et.id
          AND ed.exceedancedescription_element = ee.id
          AND ed.adjustment_type = at.id
          AND ed.area_classification = ac.id
          AND ed.exceedance_reason = er.id 
          GROUP BY
              ed.id,
              ed.exceedances,
              ed.max_value,
              ed.surface_area,
              ed.exposed_population,
              ed.population_reference_year,
              ed.vegetation_area,
              ed.other_exceedance_reason,
              ed.modelassessmentmetadata,
              a.id ,
              a.name,
              et.id::varchar ,
              et.name ,
              ee.id::varchar ,
              ee.name ,
              ed.adjustment_type,
              at.label ,
              ed.area_classification,
              ac.notation,
              ed.exceedance_reason ,
              er.label,
              ed.adjustment_source ,
              es.label
          ORDER BY a.name
        """)

        assessmentregimes = cursor.fetchall()
        return jsonify(assessmentregimes)


@exceedances_endpoint.route('/api/management/exceedances/samplingpoints', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select
              false as selected,
              null as id,
              null as exceedance_description_id,
              ad.id as assessment_data_id,
              s.name as station,
              po.notation as pollutant,
              t.label as timestep,
              u.notation as concentration,
              ar.name as assessment_regime
          from
              stations s,
              eea_pollutants po,
              sampling_points sp,
              eea_concentrations u,
              eea_times t,
              assessmentdata ad,
              assessmentregimes ar
          where 1=1
          and sp.station_id = s.id
          and sp.pollutant = po.uri
          and sp.timestep = t.id
          and sp.concentration = u.id
          and sp.id = ad.assessmentlocal_id
          and ad.assessmentregime_id = ar.id
          order by ar.name, s.name, po.notation, t.label
        """)

        assessmentregimes = cursor.fetchall()
        return jsonify(assessmentregimes)


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

        # delete and add data
        cursor.execute("delete from exceedingmethods where exceedancedescription_id = %(id)s", model)

        sql_insert = """
            insert into exceedingmethods (
                id,
                assessmentdata_id, 
                exceedancedescription_id
            )
            values (
                uuid_in(md5(random()::text || random()::text)::cstring), 
                %(assessment_data_id)s, 
                %(exceedance_description_id)s
            )
        """
        cursor.executemany(sql_insert, model.data)

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

        sql_insert = """
            insert into exceedingmethods (
                id,
                assessmentdata_id,
                exceedancedescription_id
            )
            values (
                uuid_in(md5(random()::text || random()::text)::cstring),
                %(assessment_data_id)s,
                %(exceedance_description_id)s
            )
        """
        cursor.executemany(sql_insert, model.data)

        return jsonify({"success": True})


@exceedances_endpoint.route("/api/management/exceedances/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def exceedances_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from exceedancedescriptions where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})
