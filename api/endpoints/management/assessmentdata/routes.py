"""Assessment data CRUD: which assessment methods assess which assessment regime.

This screen did not exist. `assessmentdata` was populated only by
sql/raven4_migrate/migrate_v3_to_v4.py, and the v3 app edited it inside the assessment
regime popup -- code that did not survive the v4 rewrite. So a country installing Raven
v4 fresh could create zones, sampling points and assessment regimes, and still get an
empty ComplianceAssessmentMethod, because nothing could say which method assessed which
regime. core/data/plans_programs_export.py derives CAM from exactly this table.

It is deliberately its own page rather than a sub-grid on Assessment Regime Zones. The
v3 popup deleted the regime's links and re-inserted them on every save, which silently
destroyed the `exceedingmethods` rows that cascade off them; and since 4.502.24 a link
is a period-bounded fact, which is closed rather than deleted and recreated. The
relation is also many-to-many in both directions -- a regime has many methods, and a
sampling point belongs to one regime per environmental objective -- so neither parent
owns it.

The regime page does show a regime's links again (LinkedMethods.vue, opened from a
regime's context menu), with a v3-style multi-add -- but through `candidates` and
`insert-many` below plus the per-row update and delete here, never by replacing the
regime's link set wholesale.

CAM_05 spans two tables. `assessmentlocal_id` is generated in the database from
`sampling_point_id` and `model_id`, so it is selected but never written.
"""
import psycopg2
from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException

from core.data.csv_import import csv_response, import_rows, read_csv_rows
from core.database import CursorFromPool
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                 jwt_required_with_management_claim)
from core.query import DeleteModel, Q

from .models import AssessmentDataModel

assessmentdata_endpoint = Blueprint('assessmentdata', __name__)

BASE = '/api/management/assessmentdata'

# Written by both insert and update, in one place so they cannot drift.
# `assessmentlocal_id` is absent on purpose: it is a generated column, and naming it in
# an INSERT is an error rather than a no-op.
COLUMNS = ('assessment_regime_id', 'sampling_point_id', 'model_id', 'assessmenttype',
           'assessmentmethodedescription', 'from_time', 'to_time')


def _validated(model):
    """Exactly one kind of assessment method, and a period that runs forwards.

    The database enforces both, but a constraint violation reaches the user as a 500
    naming a constraint; these say what to do about it.
    """
    if bool(model.sampling_point_id) == bool(model.model_id):
        raise BadRequest(
            'An assessment method is either a sampling point or a model, not both and '
            'not neither. AQR3 CAM_05 carries one AssessmentMethodId.')
    if model.from_time and model.to_time and model.to_time <= model.from_time:
        raise BadRequest('Valid To must be later than Valid From.')
    return model


def _derive_id(model):
    """A stable id for the link, so re-creating one does not duplicate it.

    `assessmentdata` is not an AQR3 table, so nothing mandates a format -- but the
    obvious composition (regime id plus method id) overruns varchar(100) for most
    regimes, and an operator has no reason to invent one. Derived from what the link
    IS, so the same link always gets the same id and an accidental re-add conflicts
    rather than duplicating.
    """
    import hashlib
    method = model.sampling_point_id or model.model_id
    parts = f'{model.assessment_regime_id}|{method}|{model.from_time or ""}'
    return 'AD_' + hashlib.md5(parts.encode('utf-8')).hexdigest()[:16]


@assessmentdata_endpoint.route(BASE, methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata():
    """Every link, resolved for display. Optionally narrowed to one regime."""
    regime = request.args.get('regime')

    with CursorFromPool() as cursor:
        cursor.execute(f"""
            SELECT ad.id,
                   ad.assessment_regime_id,
                   ad.sampling_point_id,
                   ad.model_id,
                   ad.assessmentlocal_id,
                   -- CAM_05 is a sampling point or a model, so it is resolved against
                   -- both. Each join is on a primary key, so neither can fan out.
                   COALESCE(m.assessment_method_name, st.name,
                            ad.assessmentlocal_id)      AS assessment_method,
                   CASE WHEN ad.model_id IS NOT NULL THEN 'Model / OBE'
                        ELSE 'Sampling point' END       AS assessment_method_kind,
                   ad.assessmenttype,
                   COALESCE(NULLIF(t.notation, ''), t.label) AS assessment_type,
                   ad.assessmentmethodedescription,
                   ad.from_time,
                   ad.to_time,
                   z.name                               AS zone_name,
                   COALESCE(NULLIF(p.notation, ''), p.label) AS regime_pollutant,
                   ot.notation                          AS objective_type,
                   rm.notation                          AS reporting_metric
            FROM assessmentdata ad
            LEFT JOIN assessment_regimes ar   ON ar.id = ad.assessment_regime_id
            LEFT JOIN zones z                 ON z.id  = ar.zone_id
            LEFT JOIN eea_pollutants p        ON p.id  = ar.pollutant_id
            LEFT JOIN eea_objectivetypes ot   ON ot.id = ar.objective_type_id
            LEFT JOIN eea_reportingmetrics rm ON rm.id = ar.reporting_metric_id
            LEFT JOIN eea_assessmenttypes t   ON t.id  = ad.assessmenttype
            LEFT JOIN models m                ON m.id  = ad.model_id
            LEFT JOIN sampling_points sp      ON sp.id = ad.sampling_point_id
            LEFT JOIN stations st             ON st.id = sp.station_id
            WHERE (%(regime)s IS NULL OR ad.assessment_regime_id = %(regime)s)
            ORDER BY ad.assessment_regime_id, ad.assessmentlocal_id, ad.from_time
        """, {'regime': regime})
        return jsonify(cursor.fetchall())


@assessmentdata_endpoint.route(f'{BASE}/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_lookups():
    """The regimes, the two kinds of assessment method, and the assessment types."""
    with CursorFromPool() as cursor:
        # Labelled by what the regime is about rather than by its identifier: the id is
        # a seven-segment string and there are hundreds of them.
        cursor.execute("""
            SELECT ar.id AS value,
                   COALESCE(z.name, ar.zone_id, '?') || ' · ' ||
                   COALESCE(NULLIF(p.notation, ''), p.label, '?') || ' · ' ||
                   COALESCE(ot.notation, '?') || '/' || COALESCE(rm.notation, '?') ||
                   COALESCE(' (' || ar.classification_year || ')', '') AS label
            FROM assessment_regimes ar
            LEFT JOIN zones z                 ON z.id  = ar.zone_id
            LEFT JOIN eea_pollutants p        ON p.id  = ar.pollutant_id
            LEFT JOIN eea_objectivetypes ot   ON ot.id = ar.objective_type_id
            LEFT JOIN eea_reportingmetrics rm ON rm.id = ar.reporting_metric_id
            ORDER BY 2
        """)
        regimes = cursor.fetchall()

        cursor.execute("""
            SELECT sp.id AS value,
                   COALESCE(st.name, '?') || ' · ' ||
                   COALESCE(NULLIF(p.notation, ''), p.label, '?') AS label
            FROM sampling_points sp
            LEFT JOIN stations st      ON st.id = sp.station_id
            LEFT JOIN eea_pollutants p ON p.id  = sp.pollutant_id
            WHERE sp.report_to_eea AND st.report_to_eea
            ORDER BY 2
        """)
        sampling_points = cursor.fetchall()

        cursor.execute("""
            SELECT id AS value,
                   id || COALESCE(' - ' || assessment_method_name, '') AS label
            FROM models ORDER BY id
        """)
        models = cursor.fetchall()

        cursor.execute("""
            SELECT id AS value, COALESCE(NULLIF(notation, ''), label) AS label
            FROM eea_assessmenttypes ORDER BY LOWER(label)
        """)
        assessment_types = cursor.fetchall()

        return jsonify({'regimes': regimes, 'sampling_points': sampling_points,
                        'models': models, 'assessment_types': assessment_types})


def _save(cursor, model):
    """Insert one link. The form's insert and the CSV import both write through here."""
    model = _validated(model)
    if not model.id:
        model = model.model_copy(update={'id': _derive_id(model)})

    columns = ', '.join(('id',) + COLUMNS)
    values = ', '.join(f'%({c})s' for c in ('id',) + COLUMNS)
    cursor.execute(
        f'INSERT INTO assessmentdata ({columns}) VALUES ({values}) '
        f'ON CONFLICT (id) DO NOTHING', model)
    if cursor.rowcount == 0:
        raise BadRequest(
            'This assessment method already assesses this regime over this period. '
            'Change the validity dates, or edit the existing link.')
    return model.id


@assessmentdata_endpoint.route(f'{BASE}/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_insert():
    with CursorFromPool() as cursor:
        id = _save(cursor, AssessmentDataModel(**request.json))
    return jsonify({'msg': 'Assessment data created successfully', 'id': id})


@assessmentdata_endpoint.route(f'{BASE}/candidates', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_candidates():
    """The methods that could still be linked to one regime, for the multi-add dialog.

    Sampling points and models measuring the regime's pollutant -- a link to anything
    else is skipped by the compliance derivation as a pollutant mismatch, so offering it
    would only invite a row that never reports. A method already linked with an
    open-ended period (no Valid To) is left out; one whose earlier link was closed is
    offered again, because re-linking it from a new date is a legitimate second period.
    """
    regime = request.args.get('regime')
    if not regime:
        raise BadRequest('regime is required')

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT ar.id, ar.pollutant_id,
                   COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant
            FROM assessment_regimes ar
            LEFT JOIN eea_pollutants p ON p.id = ar.pollutant_id
            WHERE ar.id = %s
        """, (regime,))
        found = cursor.fetchone()
        if found is None:
            raise BadRequest(f'Assessment regime {regime} does not exist.')

        # Same reporting filter as the lookups, so the dialog offers nothing the Assessment
        # data page would not.
        cursor.execute("""
            SELECT sp.id, st.name AS station_name, sp.sampling_point_reference_id,
                   sp.from_time, sp.to_time
            FROM sampling_points sp
            LEFT JOIN stations st ON st.id = sp.station_id
            WHERE sp.pollutant_id = %(pollutant)s
              AND sp.report_to_eea AND st.report_to_eea
              AND NOT EXISTS (SELECT 1 FROM assessmentdata ad
                              WHERE ad.assessment_regime_id = %(regime)s
                                AND ad.sampling_point_id = sp.id
                                AND ad.to_time IS NULL)
            ORDER BY LOWER(st.name), sp.id
        """, {'pollutant': found['pollutant_id'], 'regime': regime})
        sampling_points = cursor.fetchall()

        cursor.execute("""
            SELECT m.id, m.assessment_method_name
            FROM models m
            WHERE m.pollutant_id = %(pollutant)s
              AND NOT EXISTS (SELECT 1 FROM assessmentdata ad
                              WHERE ad.assessment_regime_id = %(regime)s
                                AND ad.model_id = m.id
                                AND ad.to_time IS NULL)
            ORDER BY m.id
        """, {'pollutant': found['pollutant_id'], 'regime': regime})
        models = cursor.fetchall()

        return jsonify({'regime': found, 'sampling_points': sampling_points,
                        'models': models})


@assessmentdata_endpoint.route(f'{BASE}/insert-many', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_insert_many():
    """Several links in one go -- the regime page's multi-add. All or nothing.

    Only ever INSERTs. The v3 popup this replaces saved a regime's whole selection by
    deleting its links and re-inserting the ticked ones, which cascaded away every
    `exceedingmethods` row hanging off them; here an existing link is never touched,
    and one that would duplicate is refused with the method named.
    """
    rows = (request.json or {}).get('rows')
    if not isinstance(rows, list) or not rows:
        raise BadRequest('rows must be a non-empty list of assessment data links')

    ids = []
    with CursorFromPool() as cursor:
        for row in rows:
            method = (row or {}).get('sampling_point_id') or (row or {}).get('model_id') or '?'
            try:
                ids.append(_save(cursor, AssessmentDataModel(**row)))
            except ValidationError as e:
                raise BadRequest(f'{method}: {e.errors()[0].get("msg")}') from e
            except HTTPException as e:
                raise BadRequest(f'{method}: {e.description}') from e
            except psycopg2.Error as e:
                # A broken reference, or the (regime, method, period) unique index.
                detail = (e.diag.message_detail or e.diag.message_primary
                          if e.diag else None) or str(e).strip()
                raise BadRequest(f'{method}: {detail}') from e
    return jsonify({'msg': f'{len(ids)} assessment method(s) linked', 'ids': ids})


@assessmentdata_endpoint.route(f'{BASE}/import', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_import():
    """One link per CSV row, with the form's checks. `id` may be left empty."""
    if 'file' not in request.files:
        raise BadRequest("File form does not contain the key 'file'")
    rows = read_csv_rows(request.files['file'], AssessmentDataModel)
    with CursorFromPool() as cursor:
        count = import_rows(cursor, rows, AssessmentDataModel, _save)
    return jsonify({'msg': f'{count} assessment data row(s) imported'})


@assessmentdata_endpoint.route(f'{BASE}/export', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_export():
    """The columns the import takes, so the file is also its template."""
    columns = ', '.join(('id',) + COLUMNS)
    with CursorFromPool() as cursor:
        cursor.execute(f'SELECT {columns} FROM assessmentdata '
                       f'ORDER BY assessment_regime_id, assessmentlocal_id, from_time')
        return csv_response(cursor.fetchall(), AssessmentDataModel, 'assessmentdata.csv')


@assessmentdata_endpoint.route(f'{BASE}/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_update():
    model = _validated(AssessmentDataModel(**request.json))
    assignments = ', '.join(f'{c} = %({c})s' for c in COLUMNS)
    with CursorFromPool() as cursor:
        cursor.execute(
            f'UPDATE assessmentdata SET {assignments} WHERE id = %(id)s', model)
        if cursor.rowcount == 0:
            raise BadRequest('Could not update assessment data ' + str(model.id))
    return jsonify({'msg': 'Assessment data updated successfully'})


@assessmentdata_endpoint.route(f'{BASE}/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_delete():
    """Deleting a link says it never happened.

    For a method that has stopped assessing a regime, set Valid To instead -- a deleted
    link takes its compliance rows with it on the next recalculation, including those
    for years already submitted.
    """
    model = DeleteModel(**request.json)
    rows = Q.delete('assessmentdata', model)
    if rows == 0:
        raise BadRequest('Could not delete for ids ' + ','.join(model.ids))
    return jsonify({'msg': 'Assessment data deleted successfully'})
