"""AQR3 SPP SamplingProcess CRUD.

Composite primary key (id, sampling_point_id, process_activity_begin) — the AQR3 key
minus CountryCode, which is instance-wide. So this does not use the generic Manager
delete: `Q.delete`'s `where id in (...)` cannot address it, and an UPDATE keyed on `id`
alone would rewrite every process sharing that ProcessId. Sharing one is the point —
SPP_02 says the same ProcessId is re-used for the same equipment configuration under
different sampling points.

Both timestamps are rendered with to_char so the string that identifies a row is the
same one the date picker round-trips, the way samplingpoints does for from_time/to_time.
"""
from flask import jsonify, Blueprint, request
from werkzeug.exceptions import BadRequest
from core.database import CursorFromPool
from core.query_access import Access
from endpoints.management.processes.models import ProcessKey, ProcessModel
from core.query import Q
from core.jwt_ext_custom import jwt_required_with_management_claim, jwt_required_with_allnetworks_claim
from core import series_metadata as smeta


processes_endpoint = Blueprint('processes', __name__)

# Written by both insert and update, in one place so the two cannot drift.
VALUES = ('process_activity_end', 'data_quality_document_id',
          'equivalence_demonstration_document_id', 'process_document_id',
          'measurement_type_id', 'method_id', 'equipment_id',
          'analytical_technique_id', 'equivalence_demonstrated_id',
          'equipment_identifier')
KEY = ('id', 'sampling_point_id', 'process_activity_begin')


def _assert_no_overlap(cursor, model, replacing=None):
    """Reject an activity period that overlaps another process on the same sampling point.

    AQR3 SPP_04: "If there is more than one ProcessId within the same AssessmentMethodId,
    then [ProcessActivityBegin] - [ProcessActivityEnd] should not overlap within the same
    AssessmentMethodId." Nothing in the schema enforces it, and two overlapping periods
    would report two different equipment configurations for the same instant with no way
    to tell which measured the data. A NULL end means "still running", so it overlaps
    everything after its start.

    Rejected rather than silently closing the earlier period: for reporting data an
    implicit edit to a row the user did not name is worse than being told to close it.
    """
    cursor.execute("""
        SELECT id,
               to_char(process_activity_begin, 'YYYY-MM-DD HH24:MI') AS begins,
               to_char(process_activity_end,   'YYYY-MM-DD HH24:MI') AS ends
        FROM processes
        WHERE sampling_point_id = %(sampling_point_id)s
          -- Skip the row being edited, identified by the key it had before this save.
          -- The IS NULL escape is load-bearing: on insert there is nothing to replace,
          -- and `NOT (id = NULL AND ...)` is NULL rather than true, which would filter
          -- out every candidate and make the guard silently pass.
          AND (%(replacing_id)s::varchar IS NULL
               OR NOT (id = %(replacing_id)s
                       AND process_activity_begin = %(replacing_begin)s::timestamp))
          AND %(process_activity_begin)s::timestamp
              < COALESCE(process_activity_end, 'infinity'::timestamp)
          AND process_activity_begin
              < COALESCE(%(process_activity_end)s::timestamp, 'infinity'::timestamp)
        ORDER BY process_activity_begin
        LIMIT 1
    """, {'sampling_point_id': model.sampling_point_id,
          'process_activity_begin': model.process_activity_begin,
          'process_activity_end': model.process_activity_end,
          'replacing_id': replacing.id if replacing else None,
          'replacing_begin': replacing.process_activity_begin if replacing else None})
    clash = cursor.fetchone()
    if clash:
        raise BadRequest(
            f'This period overlaps process {clash["id"]} on the same sampling point, '
            f'which starts {clash["begins"]} and ends '
            f'{clash["ends"] or "(still running)"}. AQR3 SPP_04 requires the periods of '
            f'two processes on one sampling point not to overlap. Close that period '
            f'first, or move this one.')


@processes_endpoint.route('/api/management/processes', methods=['GET'])
@jwt_required_with_management_claim()
def processes():
    with CursorFromPool() as cursor:
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        cursor.execute(f""" 
          {with_samplingpoints_sql}
          SELECT
              pr.id,
              -- to_char, not the raw timestamp: process_activity_begin is part of the
              -- primary key, so the string the grid holds is the one posted back to
              -- address the row. Same shape samplingpoints uses for from_time/to_time,
              -- which is also what Crud.vue's date picker emits.
              to_char(pr.process_activity_begin, 'YYYY-MM-DD HH24:MI') as process_activity_begin,
              to_char(pr.process_activity_end,   'YYYY-MM-DD HH24:MI') as process_activity_end,
              pr.data_quality_document_id, dqr.id || ' - ' || COALESCE(dqr_obj.label, '') as data_quality_document,
              pr.equivalence_demonstration_document_id, edr.id || ' - ' || COALESCE(edr_obj.label, '') as equivalence_demonstration_document,
              pr.process_document_id, pd.id || ' - ' || COALESCE(pd_obj.label, '') as process_document,
              pr.measurement_type_id, COALESCE(NULLIF(mt.notation, ''), mt.label) as measurement_type,
              pr.method_id, COALESCE(NULLIF(mm.notation, ''), mm.label) as method,
              pr.equipment_id, COALESCE(NULLIF(me.notation, ''), me.label) as equipment,
              pr.analytical_technique_id, COALESCE(NULLIF(at.notation, ''), at.label) as analytical_technique,
              pr.equivalence_demonstrated_id, COALESCE(NULLIF(ed.notation, ''), ed.label) as equivalence_demonstrated,
              pr.sampling_point_id, sp.id as sampling_point,
              -- The sampling point's own context, so the grid can lead with something
              -- readable. AQR3 reaches SPP_06 PollutantId the same way -- through the
              -- sampling point -- because `processes` has no pollutant of its own.
              s.name as station,
              COALESCE(NULLIF(po.notation, ''), po.label) as pollutant,
              t.notation as time_resolution,
              u.notation as unit,
              pr.equipment_identifier
          FROM processes pr
              LEFT JOIN eea_measurementtypes mt ON pr.measurement_type_id = mt.id
              LEFT JOIN eea_measurementmethods mm ON pr.method_id = mm.id
              LEFT JOIN eea_measurementequipments me ON pr.equipment_id = me.id
              LEFT JOIN eea_analyticaltechnique at ON pr.analytical_technique_id = at.id
              LEFT JOIN eea_equivalencedemonstrated ed ON pr.equivalence_demonstrated_id = ed.id
              LEFT JOIN documents dqr ON pr.data_quality_document_id = dqr.id
              LEFT JOIN eea_documentobject dqr_obj ON dqr.documentobject_id = dqr_obj.id
              LEFT JOIN documents edr ON pr.equivalence_demonstration_document_id = edr.id
              LEFT JOIN eea_documentobject edr_obj ON edr.documentobject_id = edr_obj.id
              LEFT JOIN documents pd ON pr.process_document_id = pd.id
              LEFT JOIN eea_documentobject pd_obj ON pd.documentobject_id = pd_obj.id
              INNER JOIN sampling_points sp ON pr.sampling_point_id = sp.id
              -- stations is inner: sampling_points.station_id is not null. The other
              -- three are nullable since migrations 012/013, so they must be LEFT or a
              -- sub-hourly or non-concentration series would drop out of the grid.
              INNER JOIN stations s ON sp.station_id = s.id
              LEFT JOIN eea_pollutants po ON sp.pollutant_id = po.id
              LEFT JOIN eea_times t ON sp.time_resolution_id = t.id
              LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
              INNER JOIN sampling_point_access spa ON sp.id = spa.id
          ORDER BY pr.id
        """, n_param)
        processes = cursor.fetchall()
        return jsonify(processes)


@processes_endpoint.route('/api/management/processes/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def processes_lookups():
    with CursorFromPool() as cursor:
        # Get sampling points accessible to user
        with_samplingpoints_sql, n_param = Q.with_sampling_points_by_networks_access()
        # Same label shape as the Validate page's timeseries select
        # (Q.timeseries_with_time_by_access) -- station, pollutant, timestep, unit, plus
        # the plugin-supplied internal comment. See core/series_metadata.py.
        pollutant = smeta.expr('pollutant', "NULLIF(po.notation, '')", 'po.label')
        timestep = smeta.expr('timestep', 't.notation')
        unit = smeta.expr('unit', 'u.notation')
        comment = smeta.expr('comment', 'NULL::text')
        cursor.execute(f"""
            {with_samplingpoints_sql}
            SELECT sp.id as value,
                   CONCAT(sp.id, ', ', s.name, ', ', {pollutant}, ', ', {timestep}, ', ', {unit}, ', ', {comment}) as label
            FROM sampling_points sp
            JOIN stations s ON sp.station_id = s.id
            LEFT JOIN eea_pollutants po ON sp.pollutant_id = po.id
            LEFT JOIN eea_times t ON sp.time_resolution_id = t.id
            LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
            {smeta.joins('sp')}
            INNER JOIN sampling_point_access spa ON sp.id = spa.id
            ORDER BY LOWER(s.name), LOWER({pollutant}), LOWER({timestep})
        """, n_param)
        sampling_points = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_measurementtypes ORDER BY LOWER(label)")
        measurement_types = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_measurementmethods ORDER BY LOWER(label)")
        methods = cursor.fetchall()
        
        cursor.execute("SELECT id as value, COALESCE(NULLIF(notation, ''), label) as label FROM eea_measurementequipments ORDER BY LOWER(COALESCE(NULLIF(notation, ''), label))")
        equipments = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_analyticaltechnique ORDER BY LOWER(label)")
        analytical_techniques = cursor.fetchall()
        
        cursor.execute("SELECT id as value, label FROM eea_equivalencedemonstrated ORDER BY LOWER(label)")
        equivalence_demonstrated = cursor.fetchall()
        
        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'samplingprocess' AND d.documentobject_id = 'dataqualityreport'
            ORDER BY d.id
        """)
        data_quality_reports = cursor.fetchall()
        
        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'samplingprocess' AND d.documentobject_id = 'equivalencedemonstrationreport'
            ORDER BY d.id
        """)
        equivalence_demonstration_reports = cursor.fetchall()
        
        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            WHERE d.datatable_id = 'samplingprocess' AND d.documentobject_id = 'processdocumentation'
            ORDER BY d.id
        """)
        process_documentations = cursor.fetchall()
        
        return jsonify({
            "sampling_points": sampling_points,
            "measurement_types": measurement_types,
            "methods": methods,
            "equipments": equipments,
            "analytical_techniques": analytical_techniques,
            "equivalence_demonstrated": equivalence_demonstrated,
            "data_quality_documents": data_quality_reports,
            "equivalence_demonstration_documents": equivalence_demonstration_reports,
            "process_documents": process_documentations
        })


@processes_endpoint.route('/api/management/processes/update', methods=['POST'])
@jwt_required_with_management_claim()
def processes_update():
    """Update one process, identified by `key`, with the values in `values`.

    All three key parts are editable, so the key travels separately: the SET clause
    writes the new key while the WHERE clause still matches the old one.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest('Body must be {key: {id, sampling_point_id, '
                         'process_activity_begin}, values: {...}}')

    key = ProcessKey(**body['key'])
    model = ProcessModel(**body['values'])

    # Both the row being moved and the row it is moving to must be reachable.
    for sampling_point_id in {key.sampling_point_id, model.sampling_point_id}:
        if not Access.to_sampling_point(sampling_point_id):
            raise BadRequest(f'Access denied for sampling point {sampling_point_id}')

    assignments = ', '.join(
        ['id = %(new_id)s',
         'sampling_point_id = %(new_sampling_point_id)s',
         'process_activity_begin = %(new_process_activity_begin)s::timestamp',
         'process_activity_end = %(process_activity_end)s::timestamp'] +
        [f'{c} = %({c})s' for c in VALUES if c != 'process_activity_end'])
    params = {c: model[c] for c in VALUES}
    params.update({f'new_{c}': model[c] for c in KEY})
    params.update({c: key[c] for c in KEY})

    with CursorFromPool() as cursor:
        _assert_no_overlap(cursor, model, replacing=key)
        cursor.execute(f"""
            UPDATE processes
            SET {assignments}
            WHERE id = %(id)s
              AND sampling_point_id = %(sampling_point_id)s
              AND process_activity_begin = %(process_activity_begin)s::timestamp
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(f'No process {key.id} on {key.sampling_point_id} starting '
                             f'{key.process_activity_begin}')

    return jsonify({"msg": "Process updated successfully"})


@processes_endpoint.route('/api/management/processes/insert', methods=['POST'])
@jwt_required_with_management_claim()
def processes_insert():
    model = ProcessModel(**(request.json or {}))

    if not Access.to_sampling_point(model.sampling_point_id):
        raise BadRequest("Access denied for sampling point")

    columns = ', '.join(KEY + VALUES)
    placeholders = ', '.join(
        ['%(id)s', '%(sampling_point_id)s', '%(process_activity_begin)s::timestamp'] +
        [f'%({c})s::timestamp' if c == 'process_activity_end' else f'%({c})s'
         for c in VALUES])

    with CursorFromPool() as cursor:
        _assert_no_overlap(cursor, model)
        cursor.execute(
            f'INSERT INTO processes ({columns}) VALUES ({placeholders})', model)

    return jsonify({"msg": "Process created successfully"}), 201


@processes_endpoint.route('/api/management/processes/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def processes_delete():
    key = ProcessKey(**(request.json or {}))

    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM processes
            WHERE id = %(id)s
              AND sampling_point_id = %(sampling_point_id)s
              AND process_activity_begin = %(process_activity_begin)s::timestamp
        """, key)
        if cursor.rowcount == 0:
            raise BadRequest(f'No process {key.id} on {key.sampling_point_id} starting '
                             f'{key.process_activity_begin}')

    return jsonify({"msg": "Process deleted successfully"})
