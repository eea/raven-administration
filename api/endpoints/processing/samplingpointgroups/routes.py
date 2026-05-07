from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query import Q
from endpoints.processing.samplingpointgroups.models import (
    CreateGroupModel, UpdateGroupModel, DeleteGroupModel, AddMemberModel, RemoveMemberModel
)
from core.jwt_ext_custom import jwt_required_with_processing_claim


spgroups_endpoint = Blueprint('spgroups', __name__)


@spgroups_endpoint.route('/api/processing/samplingpointgroups', methods=['GET'])
@jwt_required_with_processing_claim()
def list_groups():
    with CursorFromPool() as cursor:
        network_sql, n_param = Q.networks_by_access_as_sql()
        cursor.execute(f"""
            WITH
            {network_sql},
            group_members AS (
                SELECT
                    m.group_id,
                    MIN(s.name) AS station_name,
                    STRING_AGG(COALESCE(NULLIF(p.notation, ''), p.label), ', ' ORDER BY p.notation) AS members,
                    COUNT(*) AS member_count
                FROM sampling_point_group_members m
                JOIN sampling_points sp ON sp.id = m.sampling_point_id
                JOIN stations s ON sp.station_id = s.id
                JOIN eea_pollutants p ON sp.pollutant_id = p.id
                JOIN network_access n ON s.network_id = n.id
                GROUP BY m.group_id
            )
            SELECT
                spg.id,
                spg.name,
                COALESCE(gm.station_name, '') AS station,
                COALESCE(gm.members, '') AS members,
                COALESCE(gm.member_count, 0) AS member_count
            FROM sampling_point_groups spg
            LEFT JOIN group_members gm ON spg.id = gm.group_id
            ORDER BY LOWER(spg.name)
        """, n_param)
        return jsonify(cursor.fetchall())


@spgroups_endpoint.route('/api/processing/samplingpointgroups/insert', methods=['POST'])
@jwt_required_with_processing_claim()
def create_group():
    with CursorFromPool() as cursor:
        model = CreateGroupModel(**request.json)
        sp_ids = model.sampling_point_ids or []

        if sp_ids:
            station_id = None
            for sp_id in sp_ids:
                if Q.has_no_access(sp_id):
                    raise BadRequest("Access denied for sampling point")

                cursor.execute(
                    "SELECT sp.station_id FROM sampling_points sp WHERE sp.id = %(id)s",
                    {"id": sp_id}
                )
                sp = cursor.fetchone()
                if sp is None:
                    raise BadRequest("Sampling point not found")

                cursor.execute(
                    "SELECT 1 FROM sampling_point_group_members WHERE sampling_point_id = %(id)s",
                    {"id": sp_id}
                )
                if cursor.fetchone():
                    raise BadRequest("One or more sampling points are already assigned to a group")

                if station_id is None:
                    station_id = sp["station_id"]
                elif sp["station_id"] != station_id:
                    raise BadRequest("All sampling points must belong to the same station")

        cursor.execute(
            "INSERT INTO sampling_point_groups (name) VALUES (%(name)s) RETURNING id",
            model
        )
        group_id = cursor.fetchone()["id"]

        if sp_ids:
            cursor.execute(
                "INSERT INTO sampling_point_group_members (group_id, sampling_point_id) "
                "SELECT %(group_id)s, unnest(%(sp_ids)s::varchar[])",
                {"group_id": group_id, "sp_ids": sp_ids}
            )

        return jsonify({"id": group_id, "success": True})


@spgroups_endpoint.route('/api/processing/samplingpointgroups/update', methods=['POST'])
@jwt_required_with_processing_claim()
def update_group():
    with CursorFromPool() as cursor:
        model = UpdateGroupModel(**request.json)
        cursor.execute(
            "UPDATE sampling_point_groups SET name = %(name)s WHERE id = %(id)s",
            model
        )
        return jsonify({"success": True})


@spgroups_endpoint.route('/api/processing/samplingpointgroups/delete', methods=['POST'])
@jwt_required_with_processing_claim()
def delete_group():
    with CursorFromPool() as cursor:
        model = DeleteGroupModel(**request.json)
        cursor.execute("DELETE FROM sampling_point_groups WHERE id = %(id)s", model)
        return jsonify({"success": True})


@spgroups_endpoint.route('/api/processing/samplingpointgroups/<int:group_id>/members', methods=['GET'])
@jwt_required_with_processing_claim()
def list_members(group_id):
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                sp.id,
                s.id AS station_id,
                s.name AS station,
                COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant,
                COALESCE(NULLIF(t.notation, ''), t.label) AS timestep
            FROM sampling_point_group_members m
            JOIN sampling_points sp ON sp.id = m.sampling_point_id
            JOIN stations s ON sp.station_id = s.id
            JOIN eea_pollutants p ON sp.pollutant_id = p.id
            JOIN eea_times t ON sp.time_resolution_id = t.id
            WHERE m.group_id = %(group_id)s
            ORDER BY LOWER(p.notation)
        """, {"group_id": group_id})
        return jsonify(cursor.fetchall())


@spgroups_endpoint.route('/api/processing/samplingpointgroups/<int:group_id>/members/add', methods=['POST'])
@jwt_required_with_processing_claim()
def add_member(group_id):
    with CursorFromPool() as cursor:
        model = AddMemberModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for sampling point")

        cursor.execute(
            "SELECT sp.station_id FROM sampling_points sp WHERE sp.id = %(id)s",
            {"id": model.sampling_point_id}
        )
        sp = cursor.fetchone()
        if sp is None:
            raise BadRequest("Sampling point not found")

        cursor.execute(
            "SELECT 1 FROM sampling_point_group_members WHERE sampling_point_id = %(id)s",
            {"id": model.sampling_point_id}
        )
        if cursor.fetchone():
            raise BadRequest("Sampling point is already assigned to a group")

        cursor.execute(
            "SELECT sp.station_id FROM sampling_point_group_members m "
            "JOIN sampling_points sp ON sp.id = m.sampling_point_id "
            "WHERE m.group_id = %(group_id)s LIMIT 1",
            {"group_id": group_id}
        )
        existing = cursor.fetchone()
        if existing and sp["station_id"] != existing["station_id"]:
            raise BadRequest("Sampling point must belong to the same station as the group members")

        cursor.execute(
            "INSERT INTO sampling_point_group_members (group_id, sampling_point_id) VALUES (%(group_id)s, %(id)s)",
            {"group_id": group_id, "id": model.sampling_point_id}
        )
        return jsonify({"success": True})


@spgroups_endpoint.route('/api/processing/samplingpointgroups/<int:group_id>/members/remove', methods=['POST'])
@jwt_required_with_processing_claim()
def remove_member(group_id):
    with CursorFromPool() as cursor:
        model = RemoveMemberModel(**request.json)

        if Q.has_no_access(model.sampling_point_id):
            raise BadRequest("Access denied for sampling point")

        cursor.execute(
            "DELETE FROM sampling_point_group_members WHERE sampling_point_id = %(id)s AND group_id = %(group_id)s",
            {"id": model.sampling_point_id, "group_id": group_id}
        )
        return jsonify({"success": True})


@spgroups_endpoint.route('/api/processing/samplingpointgroups/lookup/samplingpoints', methods=['GET'])
@jwt_required_with_processing_claim()
def lookup_samplingpoints():
    group_id = request.args.get('group_id', type=int)
    with CursorFromPool() as cursor:
        network_sql, n_param = Q.networks_by_access_as_sql()
        params = {**n_param}
        if group_id is not None:
            member_filter = "m.sampling_point_id IS NULL OR m.group_id = %(group_id)s"
            params["group_id"] = group_id
        else:
            member_filter = "m.sampling_point_id IS NULL"
        cursor.execute(f"""
            WITH
            {network_sql}
            SELECT
                sp.id AS value,
                sp.station_id,
                CONCAT(s.name, ', ', COALESCE(NULLIF(p.notation, ''), p.label), ', ', COALESCE(NULLIF(t.notation, ''), t.label), ', ', u.notation) AS label
            FROM sampling_points sp
            JOIN stations s ON sp.station_id = s.id
            JOIN eea_pollutants p ON sp.pollutant_id = p.id
            JOIN eea_times t ON sp.time_resolution_id = t.id
            JOIN eea_concentrations u ON sp.unit_id = u.id
            JOIN network_access n ON s.network_id = n.id
            LEFT JOIN sampling_point_group_members m ON m.sampling_point_id = sp.id
            WHERE ({member_filter})
              AND sp.from_time IS NOT NULL
              AND sp.to_time IS NOT NULL
            ORDER BY LOWER(s.name), LOWER(p.notation)
        """, params)
        return jsonify(cursor.fetchall())
