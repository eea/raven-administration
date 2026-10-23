import logging
import threading

from flask import jsonify, Blueprint, request
from endpoints.misc.preaggregation.models import AggModel
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q
preagg_endpoint = Blueprint('preagg', __name__)

logger = logging.getLogger(__name__)

# Held for the whole refresh, by this endpoint and by cron/refresh_views.py, so the two
# never refresh at once and the page can tell that one is running. Transaction-scoped
# (pg_try_advisory_xact_lock), so it is released at commit and can never stay behind on
# a pooled connection. cron/refresh_views.py repeats the number.
REFRESH_LOCK = 4502025


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
            order by 1
        """
        cursor.execute(sql)
        values = cursor.fetchall()
        return jsonify(values)


def _refresh_running(cursor):
    cursor.execute("""
        select exists (select 1 from pg_locks
                        where locktype = 'advisory' and classid = 0
                          and objid = %(key)s and objsubid = 1) as running
    """, {'key': REFRESH_LOCK})
    return cursor.fetchone()['running']


def _refresh():
    try:
        with CursorFromPool() as cursor:
            cursor.execute('select pg_try_advisory_xact_lock(%(key)s) as locked',
                           {'key': REFRESH_LOCK})
            if not cursor.fetchone()['locked']:
                logger.info('Pre-aggregation refresh already running; not starting another')
                return
            cursor.execute('select raven_refresh_aggregates()')
        logger.info('Pre-aggregation refresh finished')
    except Exception:
        logger.exception('Pre-aggregation refresh failed')


# The refresh outlives an HTTP request: ten materialized views over every observation
# took longer than the ingress waits, so the page reported a failure while the database
# went on and finished. It runs in the background now, and the page polls /status.
@preagg_endpoint.route('/api/misc/preaggregation/update', methods=['GET'])
@jwt_required_with_management_claim()
def preagg_update():
    with CursorFromPool() as cursor:
        if _refresh_running(cursor):
            return jsonify({'running': True})
    threading.Thread(target=_refresh, name='preaggregation-refresh', daemon=True).start()
    return jsonify({'started': True, 'running': True}), 202


@preagg_endpoint.route('/api/misc/preaggregation/status', methods=['GET'])
@jwt_required_with_management_claim()
def preagg_status():
    with CursorFromPool() as cursor:
        return jsonify({'running': _refresh_running(cursor)})
