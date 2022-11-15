from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.assessmentregimes.models import AssessmentRegimeModel, DeleteModel
from api.core.jwt_ext_custom import jwt_required_with_management_claim


assessmentregimes_endpoint = Blueprint('assessmentregimes', __name__)


@assessmentregimes_endpoint.route('/api/management/assessmentregimes', methods=['GET'])
@jwt_required_with_management_claim()
def assessmentregimes():
    with CursorFromPool() as cursor:
        cursor.execute("""
          SELECT
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
              assessmentregimes ar,
              zones z,
              eea_pollutants po,
              eea_objecttypes ot,
              eea_reportingmetrics rm,
              eea_protectiontargets pt,
              eea_assessmentthresholdexceedances e
          WHERE 1=1
          AND ar.zoneid = z.id
          AND ar.pollutant = po.uri
          AND ar.objecttype = ot.id
          AND ar.reportingmetric = rm.id
          AND ar.protectiontarget = pt.id
          AND ar.assessmentthresholdexceedance = e.id
          ORDER BY z.name, po.notation, ar.objecttype, ar.reportingmetric, ar.protectiontarget, ar.thresholdclassificationyear
        """)

        assessmentregimes = cursor.fetchall()

        cursor.execute("""
        select
              d.assessmentregime_id,
              d.assessmentlocal_id as samplingpoint_id,
              s.name as station_name,
              po.notation as pollutant,
              d.assessmenttype as "assessmenttype",
              d.assessmentmethodedescription as "description",
              true as "selected"
          from assessmentdata d, stations s, sampling_points sp, eea_pollutants po
          where 1=1
          and sp.station_id = s.id
          and sp.pollutant = po.uri
          and d.assessmentlocal_id = sp.id
        """)
        data = cursor.fetchall()

        for r in assessmentregimes:
            d = list(filter(lambda p: p["assessmentregime_id"] == r["id"], data))
            r["data"] = d

        return jsonify(assessmentregimes)


@assessmentregimes_endpoint.route('/api/management/assessmentregime/update', methods=['POST'])
@jwt_required_with_management_claim()
def assessmentregimes_update():
    with CursorFromPool() as cursor:
        model = AssessmentRegimeModel(**request.json)
        sql = """            

        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not update for id " + model.id)

        return jsonify({"success": True})


@assessmentregimes_endpoint.route('/api/management/assessmentregime/insert', methods=['POST'])
@jwt_required_with_management_claim()
def assessmentregimes_insert():
    with CursorFromPool() as cursor:
        model = AssessmentRegimeModel(**request.json)
        sql = """
                
        """
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not insert for id " + model.id)
        return jsonify({"success": True})


@assessmentregimes_endpoint.route("/api/management/assessmentregime/delete", methods=['POST'])
@jwt_required_with_management_claim()
def assessmentregimes_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from assessmentregimes where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})
