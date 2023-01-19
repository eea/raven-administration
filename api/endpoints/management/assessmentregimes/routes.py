from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from endpoints.management.assessmentregimes.models import AssessmentRegimeModel
from core.query import Q, DeleteModel
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim


assessmentregimes_endpoint = Blueprint('assessmentregimes', __name__)


@assessmentregimes_endpoint.route('/api/management/assessmentregimes', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes():
    with CursorFromPool() as cursor:
        cursor.execute("""
          WITH data as (
              select
                  true as selected,
                  ad.id as id,
                  ad.assessmenttype as assessment_type_id,
                  ad.assessmentmethodedescription as description,
                  ad.assessmentregime_id as assessment_regime_id,
                  sp.id as sampling_point_id,
                  s.name as station,
                  po.notation as pollutant,
                  po.uri as pollutant_id,
                  t.label as timestep,
                  u.notation as concentration
              from
                  stations s,
                  eea_pollutants po,
                  assessmentdata ad,
                  sampling_points sp,
                  eea_concentrations u,
                  eea_times t
              where 1=1
              and sp.station_id = s.id
              and sp.pollutant = po.uri
              and sp.timestep = t.id
              and sp.concentration = u.id
              and sp.id = ad.assessmentlocal_id
              and sp.private = false
          )
          SELECT
              case when count(d.sampling_point_id) = 0 then '[]' else json_agg(d) end as data,
              count(d.sampling_point_id) spo_count,
              ar.id,
              ar.name,
              z.id as zone_id,
              z.name as zone,
              ar.pollutant as pollutant_id,
              po.notation as pollutant,
              ar.objecttype as object_type_id,
              ot.id as object_type,
              ar.reportingmetric as reporting_metric_id,
              rm.id as reporting_metric,
              ar.protectiontarget as protection_target_id,
              pt.id as protection_target,
              ar.assessmentthresholdexceedance as exceedance_id,
              e.id as exceedance,
              ar.thresholdclassificationyear as year,
              ar.thresholdclassificationreport as report,
              ar.include
          FROM
              zones z,
              eea_pollutants po,
              eea_objecttypes ot,
              eea_reportingmetrics rm,
              eea_protectiontargets pt,
              eea_assessmentthresholdexceedances e,
              assessmentregimes ar left outer join data d on ar.id = d.assessment_regime_id
          WHERE 1=1
          AND ar.zoneid = z.id
          AND ar.pollutant = po.uri
          AND ar.objecttype = ot.id
          AND ar.reportingmetric = rm.id
          AND ar.protectiontarget = pt.id
          AND ar.assessmentthresholdexceedance = e.id
          GROUP BY
              ar.id,
              ar.name,
              z.id  ,
              z.name ,
              ar.pollutant ,
              po.notation ,
              ar.objecttype ,
              ot.id ,
              ar.reportingmetric ,
              rm.id ,
              ar.protectiontarget,
              pt.id,
              ar.assessmentthresholdexceedance ,
              e.id ,
              ar.thresholdclassificationyear,
              ar.thresholdclassificationreport ,
              ar.include
          ORDER BY z.name, po.notation, ar.objecttype, ar.reportingmetric, ar.protectiontarget, ar.thresholdclassificationyear
        """)

        assessmentregimes = cursor.fetchall()
        return jsonify(assessmentregimes)


@assessmentregimes_endpoint.route('/api/management/assessmentregime/samplingpoints', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def samplingpoints():
    with CursorFromPool() as cursor:
        cursor.execute("""
          select
              false as selected,
              null as id,
              null as assessment_type_id,
              null as description,
              null as assessment_regime_id,
              sp.id as sampling_point_id,
              s.name as station,
              po.notation as pollutant,
              po.uri as pollutant_id,
              t.label as timestep,
              u.notation as concentration
          from
              stations s,
              eea_pollutants po,
              sampling_points sp,
              eea_concentrations u,
              eea_times t
          where 1=1
          and sp.station_id = s.id
          and sp.pollutant = po.uri
          and sp.timestep = t.id
          and sp.concentration = u.id
          and sp.private = false
          order by s.name, po.notation, t.label
        """)

        assessmentregimes = cursor.fetchall()
        return jsonify(assessmentregimes)


@assessmentregimes_endpoint.route('/api/management/assessmentregime/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_update():
    with CursorFromPool() as cursor:
        model = AssessmentRegimeModel(**request.json)

        # Update assessment regime
        sql_update = """
          UPDATE assessmentregimes
          SET
            name=%(name)s,
            assessmentthresholdexceedance=%(exceedance_id)s,
            thresholdclassificationyear=%(year)s,
            thresholdclassificationreport=%(report)s,
            include=%(include)s
          WHERE id = %(id)s
        """
        cursor.execute(sql_update, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        # delete and add assessment regime data
        cursor.execute("delete from assessmentdata where assessmentregime_id = %(id)s", model)

        sql_insert = """
            insert into assessmentdata (
                id,
                assessmentregime_id,
                assessmentlocal_id,
                assessmenttype,
                assessmentmethodedescription
            )
            values (
                uuid_in(md5(random()::text || random()::text)::cstring),
                %(assessment_regime_id)s,
                %(sampling_point_id)s,
                %(assessment_type_id)s,
                %(description)s
            )
        """
        cursor.executemany(sql_insert, model.data)

        return jsonify({"success": True})


@assessmentregimes_endpoint.route('/api/management/assessmentregime/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_insert():
    with CursorFromPool() as cursor:
        model = AssessmentRegimeModel(**request.json)
        sql = """
            insert into assessmentregimes (
                id,
                name,
                zoneid,
                pollutant,
                objecttype,
                reportingmetric,
                protectiontarget,
                assessmentthresholdexceedance,
                include,
                thresholdclassificationyear,
                thresholdclassificationreport
            )
            values (
                %(id)s,
                %(name)s,
                %(zone_id)s,
                %(pollutant_id)s,
                %(object_type_id)s,
                %(reporting_metric_id)s,
                %(protection_target_id)s,
                %(exceedance_id)s,
                %(include)s,
                %(year)s,
                %(report)s
            )
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)

        sql_insert = """
            insert into assessmentdata (
                id,
                assessmentregime_id,
                assessmentlocal_id,
                assessmenttype,
                assessmentmethodedescription
            )
            values (
                uuid_in(md5(random()::text || random()::text)::cstring),
                %(assessment_regime_id)s,
                %(sampling_point_id)s,
                %(assessment_type_id)s,
                %(description)s
            )
        """
        cursor.executemany(sql_insert, model.data)

        return jsonify({"success": True})


@assessmentregimes_endpoint.route("/api/management/assessmentregime/delete", methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentregimes_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete("assessmentregimes", model)
    if rows == 0:
        raise BadRequest("Could not delete for ids " + {','.join(model.ids)})
    return jsonify({"success": True})
