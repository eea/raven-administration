from flask import jsonify, Blueprint, request
from endpoints.misc.notifications.models import NotificationsModel, DeleteModel
from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core.query import Q
notifications_endpoint = Blueprint('notifications', __name__)


@notifications_endpoint.route('/api/misc/notifications', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def notifications():
    with CursorFromPool() as cursor:
        sql = """
            SELECT 
              n.*,
              COALESCE(
                array_agg(ns.sampling_point_id) FILTER (WHERE ns.sampling_point_id IS NOT NULL),
                '{}'
              ) AS sampling_points
            FROM notifications n
            LEFT JOIN notifications_samplingpoints ns ON n.name = ns.notification_id
            GROUP BY n.name
            ORDER BY LOWER(n.name)

        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@notifications_endpoint.route('/api/misc/notifications/logs', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def notifications_logs():
    with CursorFromPool() as cursor:
        sql = """
          select
                to_char(run_timestamp,'yyyy-mm-dd HH24:mi') as run_timestamp,
                missing_data_count,
                notifications_sent,
                notifications_failed,
                smtp_server,
                execution_time_ms,
                status,
                error_message
          from notifications_runs
          order by run_timestamp desc
          limit 5

        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@notifications_endpoint.route('/api/misc/notifications/missing_values', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def missing_values():
    with CursorFromPool() as cursor:
        sql = """
            select 
                sp.id as spo,
                s.name as station, 
                COALESCE(NULLIF(p.notation, ''), p.label) as pollutant, 
                c.notation as concentration, 
                t.label as timestep, 
                to_char(sp.to_time,'yyyy-mm-dd HH24:mi') as totime
            from sampling_points sp
            join stations s on sp.station_id = s.id
            join eea_pollutants p on sp.pollutant_id = p.id
            join eea_concentrations c on sp.unit_id = c.id
            join eea_times t on sp.time_resolution_id = t.id
            where sp.to_time is not null
            and sp.to_time < now() - interval '3 hours'
            order by station, pollutant

        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@notifications_endpoint.route('/api/misc/notifications/sampling_points', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def sampling_points():
    with CursorFromPool() as cursor:
        sql = """
            select 
                sp.id as spo,
                s.name as station, 
                COALESCE(NULLIF(p.notation, ''), p.label) as pollutant, 
                c.notation as concentration, 
                t.label as timestep
            from sampling_points sp
            join stations s on sp.station_id = s.id
            join eea_pollutants p on sp.pollutant_id = p.id
            join eea_concentrations c on sp.unit_id = c.id
            join eea_times t on sp.time_resolution_id = t.id
            order by station, pollutant
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        return jsonify(rows)


@notifications_endpoint.route('/api/misc/notifications/save', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def save_notification():
    model = NotificationsModel(**request.json)
    with CursorFromPool() as cursor:
        # delete notification if exists where neme = model.originalname
        if model.originalname:
            sql = "DELETE FROM notifications WHERE name = %s"
            cursor.execute(sql, (model.originalname,))

        # insert new notification
        sql = "INSERT INTO notifications (name, emails, enabled) VALUES (%s, %s, %s)"
        cursor.execute(sql, (model.name, model.emails, model.enabled))

        # insert sampling points
        if model.sampling_points:
            sql = "INSERT INTO notifications_samplingpoints (notification_id, sampling_point_id) VALUES (%s, %s)"
            for sp in model.sampling_points:
                cursor.execute(sql, (model.name, sp))

        return jsonify({"success": True})


@notifications_endpoint.route('/api/misc/notifications/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def delete_notification():
    model = DeleteModel(**request.json)
    with CursorFromPool() as cursor:
        # delete notification where name = model.name
        sql = "DELETE FROM notifications WHERE name = %s"
        cursor.execute(sql, (model.name,))
        return jsonify({"success": True})
