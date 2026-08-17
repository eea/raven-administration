"""AQR3 ADJ PollutionLevelAdjustment CRUD.

`pollution_level_adjustment` was referenced only by the export: migration 003
created the table and backfilled two of its four columns from
exceedancedescriptions, and nothing has written it since. So an adjusted pollution
level could be reported (CAM_11) without the deduction behind it ever being
justified.

Composite primary key (attainment_id, adjustment_source_id), so this does not use
the generic Manager delete — `Q.delete`'s `where id in (...)` cannot address it.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.jwt_ext_custom import (jwt_required_with_allnetworks_claim,
                                jwt_required_with_management_claim)

from .models import AdjustmentKey, AdjustmentModel

adjustments_endpoint = Blueprint('pollutionleveladjustment', __name__)

BASE = '/api/management/pollutionleveladjustment'

VALUES = ('adjustment_assessment_method_id', 'adjustment_document_id')


def _assert_method_is_source_specific(cursor, model, replacing=None):
    """The guide requires a different method per AdjustmentSource.

    'AdjustmentAssessmentMethodId must be different for each AdjustmentSource so
    that it is possible to report adjustment values for each of them in the
    MOEResult tables' — sharing one method between two sources makes the per-source
    deductions indistinguishable in MRI/MRE.
    """
    if not model.adjustment_assessment_method_id:
        return
    cursor.execute("""
        SELECT adjustment_source_id
        FROM pollution_level_adjustment
        WHERE attainment_id = %(attainment_id)s
          AND adjustment_assessment_method_id = %(method)s
          AND adjustment_source_id <> %(source)s
          AND (%(replacing)s::varchar IS NULL OR adjustment_source_id <> %(replacing)s)
        LIMIT 1
    """, {'attainment_id': model.attainment_id,
          'method': model.adjustment_assessment_method_id,
          'source': model.adjustment_source_id,
          'replacing': replacing})
    clash = cursor.fetchone()
    if clash:
        raise BadRequest(
            f'Assessment method {model.adjustment_assessment_method_id} is already used for '
            f'adjustment source {clash["adjustment_source_id"]} on this attainment. AQR3 '
            f'requires a different method per source, so the deduction for each can be '
            f'reported separately in the MOEResult tables.')


@adjustments_endpoint.route(BASE, methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def adjustments():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT a.attainment_id,
                   a.adjustment_source_id,
                   COALESCE(NULLIF(ast.notation, ''), ast.label) AS adjustment_source,
                   ast.label AS adjustment_source_label,
                   a.adjustment_assessment_method_id,
                   a.adjustment_document_id
            FROM pollution_level_adjustment a
            LEFT JOIN eea_adjustmentsourcetype ast ON a.adjustment_source_id = ast.id
            ORDER BY a.attainment_id, a.adjustment_source_id
        """)
        return jsonify(cursor.fetchall())


@adjustments_endpoint.route(f'{BASE}/lookups', methods=['GET'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def adjustments_lookups():
    with CursorFromPool() as cursor:
        # The 16 permitted causes: sea spray, Saharan dust, wildfires, volcanic and
        # seismic activity, high-wind resuspension, each inside/outside the state.
        cursor.execute("""
            SELECT id AS value,
                   COALESCE(NULLIF(label, ''), notation) || ' (' || id || ')' AS label
            FROM eea_adjustmentsourcetype ORDER BY id
        """)
        sources = cursor.fetchall()

        # ADJ_02 must match an attainment that compliance produced.
        cursor.execute("""
            SELECT DISTINCT attainment_id AS value, attainment_id AS label
            FROM compliance_assessment_method
            WHERE attainment_id IS NOT NULL
            ORDER BY attainment_id
        """)
        attainments = cursor.fetchall()

        # ADJ_04 points at the model/OBE that quantified the deduction.
        cursor.execute("""
            SELECT id AS value,
                   id || COALESCE(' - ' || assessment_method_name, '') AS label
            FROM models ORDER BY id
        """)
        methods = cursor.fetchall()

        cursor.execute("""
            SELECT d.id AS value, d.id || ' - ' || COALESCE(dobj.label, '') AS label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            ORDER BY d.id
        """)
        documents = cursor.fetchall()

    return jsonify({'adjustment_sources': sources, 'attainments': attainments,
                    'methods': methods, 'documents': documents})


@adjustments_endpoint.route(f'{BASE}/insert', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def insert():
    model = AdjustmentModel(**request.json)
    columns = ('attainment_id', 'adjustment_source_id') + VALUES
    with CursorFromPool() as cursor:
        _assert_method_is_source_specific(cursor, model)
        cursor.execute(f"""
            INSERT INTO pollution_level_adjustment ({', '.join(columns)})
            VALUES ({', '.join(f'%({c})s' for c in columns)})
        """, model)
    return jsonify({'msg': 'Adjustment created successfully'}), 201


@adjustments_endpoint.route(f'{BASE}/update', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def update():
    """Update one adjustment, identified by `key`, with the values in `values`.

    Both key parts are editable, so the key travels separately: an UPDATE keyed on
    the new values would match nothing and leave the original row in place.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest("Body must be {key: {attainment_id, adjustment_source_id}, "
                         "values: {...}}")

    key = AdjustmentKey(**body['key'])
    model = AdjustmentModel(**body['values'])

    assignments = ', '.join(['attainment_id = %(new_attainment_id)s',
                             'adjustment_source_id = %(new_adjustment_source_id)s'] +
                            [f'{c} = %({c})s' for c in VALUES])
    params = {c: model[c] for c in VALUES}
    params.update(new_attainment_id=model.attainment_id,
                  new_adjustment_source_id=model.adjustment_source_id,
                  attainment_id=key.attainment_id,
                  adjustment_source_id=key.adjustment_source_id)

    with CursorFromPool() as cursor:
        _assert_method_is_source_specific(cursor, model, replacing=key.adjustment_source_id)
        cursor.execute(f"""
            UPDATE pollution_level_adjustment
            SET {assignments}
            WHERE attainment_id = %(attainment_id)s
              AND adjustment_source_id = %(adjustment_source_id)s
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(f'No adjustment for {key.attainment_id} / '
                             f'{key.adjustment_source_id}')
    return jsonify({'msg': 'Adjustment updated successfully'})


@adjustments_endpoint.route(f'{BASE}/delete', methods=['POST'])
@jwt_required_with_management_claim()
@jwt_required_with_allnetworks_claim()
def delete():
    key = AdjustmentKey(**(request.json or {}))
    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM pollution_level_adjustment
            WHERE attainment_id = %(attainment_id)s
              AND adjustment_source_id = %(adjustment_source_id)s
        """, key)
        if cursor.rowcount == 0:
            raise BadRequest(f'No adjustment for {key.attainment_id} / '
                             f'{key.adjustment_source_id}')
    return jsonify({'msg': 'Adjustment deleted successfully'})
