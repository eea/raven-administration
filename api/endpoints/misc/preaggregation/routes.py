from flask import jsonify, Blueprint, request
from endpoints.misc.preaggregation.models import AggModel
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q
preagg_endpoint = Blueprint('preagg', __name__)


@preagg_endpoint.route('/api/misc/preaggregation', methods=['GET'])
@jwt_required_with_management_claim()
def preagg():
    with CursorFromPool() as cursor:
        sql = f"""
            select 'year' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_year
            union
            select 'day' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_day
            union
            select 'winter season' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time,to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_winter_season
            union
            select 'winter year' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_winter_year
            union
            select 'summer year' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_summer_year
            union
            select 'aot40 vegetation' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_aot40v
            union
            select 'aot40 forrest' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_aot40f
            union
            select 'day 8h max' as type, round(avg(cov)) as avg_cov, count(*) as count_val, count(distinct sampling_point_id) count_sp, to_char(min(time),'yyyy-mm-dd HH24:mi') as first_time, to_char(max(time),'yyyy-mm-dd HH24:mi') as last_time, to_char(max(created),'yyyy-mm-dd HH24:mi') as created from observations_day_8hmax
            order by LOWER(type)
        """
        cursor.execute(sql)
        values = cursor.fetchall()
        return jsonify(values)


@preagg_endpoint.route('/api/misc/preaggregation/update', methods=['GET'])
@jwt_required_with_management_claim()
def preagg_update():
    with CursorFromPool() as cursor:
        cursor.execute("select raven_refresh_aggregates();")
        return jsonify({'message': 'success'})
