from flask import jsonify, Blueprint, request, Response
from core.database import CursorFromPool
from core.data.management import Management
from core.jwt_ext_custom import jwt_required_with_allnetworks_claim, jwt_required_with_management_claim
from core.utils import U

export_management_endpoint = Blueprint('export_management', __name__)


@export_management_endpoint.route('/api/exports/authorities', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_authorities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "responsible_authorities")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "authorities.csv")


@export_management_endpoint.route('/api/exports/zones', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_zones():
    with CursorFromPool() as cursor:
        m = Management(cursor, "zones")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "zones.csv")


@export_management_endpoint.route('/api/exports/networks', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_networks():
    with CursorFromPool() as cursor:
        m = Management(cursor, "networks")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "networks.csv")


@export_management_endpoint.route('/api/exports/stations', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_stations():
    with CursorFromPool() as cursor:
        m = Management(cursor, "stations")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "stations.csv")


@export_management_endpoint.route('/api/exports/sampling_points', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_sampling_points():
    with CursorFromPool() as cursor:
        m = Management(cursor, "sampling_points", ["from_time", "to_time"])
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "sampling_points.csv")


@export_management_endpoint.route('/api/exports/observing_capabilities', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_observing_capabilities():
    with CursorFromPool() as cursor:
        m = Management(cursor, "observing_capabilities")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "observing_capabilities.csv")


@export_management_endpoint.route('/api/exports/samples', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def export_samples():
    with CursorFromPool() as cursor:
        m = Management(cursor, "samples")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "samples.csv")


@export_management_endpoint.route('/api/exports/processes', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_processes():
    with CursorFromPool() as cursor:
        m = Management(cursor, "processes")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "processes.csv")


@export_management_endpoint.route('/api/exports/attainments', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_attainments():
    with CursorFromPool() as cursor:
        m = Management(cursor, "attainments")
        m.generic_select()
        return U.dataframe_to_csv_response(m.df, "attainments.csv")


@export_management_endpoint.route('/api/exports/assessmentregime', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_assessmentregime():
    with CursorFromPool() as cursor:
        m = Management(cursor, "assessmentregime")
        sql = """
          select ar.*, json_agg(ad.*) as assessmentdata
          from assessmentregimes ar, assessmentdata ad
          where ar.id = ad.assessmentregime_id
          group by
            ar.id,
            ar.name,
            ar.zoneid,
            ar.pollutant,
            ar.objecttype,
            ar.reportingmetric,
            ar.protectiontarget,
            ar.assessmentthresholdexceedance,
            ar.include,
            ar.thresholdclassificationyear,
            ar.thresholdclassificationreport
        """
        m.sql_select(sql)
        return U.dataframe_to_csv_response(m.df, "assessmentregime.csv")


@export_management_endpoint.route('/api/exports/exceedances', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def import_exceedances():
    with CursorFromPool() as cursor:
        m = Management(cursor, "exceedances")
        sql = """
          select ed.*, json_agg(em.*) as exceedingmethods
          from exceedancedescriptions ed, exceedingmethods em
          where ed.id = em.exceedancedescription_id
          group by
              ed.id,
              ed.exceedances,
              ed.max_value,
              ed.surface_area,
              ed.exposed_population,
              ed.population_reference_year,
              ed.vegetation_area,
              ed.other_exceedance_reason,
              ed.modelassessmentmetadata,
              ed.adjustment_type,
              ed.area_classification,
              ed.exceedance_reason ,
              ed.adjustment_source
        """
        m.sql_select(sql)
        return U.dataframe_to_csv_response(m.df, "exceedances.csv")
