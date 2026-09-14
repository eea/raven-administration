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

CAM_05 spans two tables. `assessmentlocal_id` is generated in the database from
`sampling_point_id` and `model_id`, so it is selected but never written.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

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


@assessmentdata_endpoint.route(f'{BASE}/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def assessmentdata_insert():
    model = _validated(AssessmentDataModel(**request.json))
    if not model.id:
        model = model.model_copy(update={'id': _derive_id(model)})

    columns = ', '.join(('id',) + COLUMNS)
    values = ', '.join(f'%({c})s' for c in ('id',) + COLUMNS)
    with CursorFromPool() as cursor:
        cursor.execute(
            f'INSERT INTO assessmentdata ({columns}) VALUES ({values}) '
            f'ON CONFLICT (id) DO NOTHING', model)
        if cursor.rowcount == 0:
            raise BadRequest(
                'This assessment method already assesses this regime over this period. '
                'Change the validity dates, or edit the existing link.')

    return jsonify({'msg': 'Assessment data created successfully', 'id': model.id})


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
