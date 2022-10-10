from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.exceptions import BadRequest
from api.core.database import CursorFromPool
from api.endpoints.management.assessmentregimes.models import AssessmentRegimeModel, DeleteModel


assessmentregimes_endpoint = Blueprint('assessmentregimes', __name__)


@assessmentregimes_endpoint.route('/api/management/assessmentregimes', methods=['GET'])
@jwt_required()
def assessmentregimes():
    with CursorFromPool() as cursor:
        cursor.execute("""
          SELECT
            ar.id, ar.name,
            ar.objecttype, ar.reportingmetric, ar.protectiontarget,
            ar.assessmentthresholdexceedance, ar.include, ar.thresholdclassificationyear, ar.thresholdclassificationreport,
            z.id as zoneid, z.name as zone_name, ar.pollutant, po.notation as pollutant_name
        FROM assessmentregimes ar
            LEFT JOIN zones z ON ar.zoneid = z.id
            LEFT JOIN eea_pollutants po on ar.pollutant = po.uri
        ORDER BY ar.thresholdclassificationyear, z.name, po.notation, ar.objecttype, ar.reportingmetric, ar.protectiontarget
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
@jwt_required()
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
@jwt_required()
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
@jwt_required()
def assessmentregimes_delete():
    with CursorFromPool() as cursor:
        model = DeleteModel(**request.json)
        sql = "delete from assessmentregimes where id = %(id)s"
        cursor.execute(sql, model)
        if cursor.rowcount == 0:
            raise BadRequest("Could not delete for id " + model.id)

        return jsonify({"success": True})
