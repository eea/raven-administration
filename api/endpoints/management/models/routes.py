"""Models / objective estimation (AQR3 MOE) management, plus gridded result ingest.

raven-admin had no model concept at all: everything assumed a measurement at a
sampling point. AQR3 v5.02 needs MOD_/OBE_ assessment methods for ModelObjectiveEstimation
and for the model-based rows of ComplianceAssessmentMethod, SpatialRepresentativeness
and PollutionLevelAdjustment.
"""
import os
import tempfile

from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.eea.id_generator import IdentifierError, validate_identifier
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q, DeleteModel
from core.reporting.aqr3.grid import (
    GridError,
    points_to_inspire_grid,
    to_inspire_grid,
    validate_resolution,
)

from core.reporting.aqr3.attachments import AttachmentReferenceError, validate_reference
from .models import (ExternalResultKey, ExternalResultModel,
                     ModelObjectiveEstimationModel, ModelResultUploadModel)

models_endpoint = Blueprint('models', __name__)

# Same guard the SR upload uses: a fine raster over a country is easily millions
# of cells, which is not something to push through a single request.
MAX_CELLS = 500_000


@models_endpoint.route('/api/management/models', methods=['GET'])
@jwt_required_with_management_claim()
def models():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT m.id,
                   m.data_aggregation_process_id,
                   m.assessment_method_name,
                   m.pollutant_id, COALESCE(NULLIF(p.notation, ''), p.label) as pollutant,
                   m.result_encoding_id, re.notation as result_encoding,
                   m.method_application_id, ma.notation as method_application,
                   m.generic_mqi,
                   m.data_quality_document_id,
                   m.method_document_id,
                   (SELECT COUNT(*) FROM moe_result_external e
                     WHERE e.assessment_method_id = m.id) as external_result_count
            FROM models m
            LEFT JOIN eea_pollutants p        ON m.pollutant_id          = p.id
            LEFT JOIN eea_resultencoding re   ON m.result_encoding_id    = re.id
            LEFT JOIN eea_modelapplication ma ON m.method_application_id = ma.id
            ORDER BY m.id
        """)
        return jsonify(cursor.fetchall())


@models_endpoint.route('/api/management/models/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def models_lookups():
    with CursorFromPool() as cursor:
        pollutants = Q.pollutants_lookup()

        cursor.execute("SELECT id as value, COALESCE(NULLIF(notation, ''), label) as label "
                       "FROM eea_aggregationprocess ORDER BY id")
        aggregation_processes = cursor.fetchall()

        cursor.execute("SELECT id as value, label FROM eea_resultencoding ORDER BY label")
        result_encodings = cursor.fetchall()

        cursor.execute("SELECT id as value, label FROM eea_modelapplication ORDER BY label")
        method_applications = cursor.fetchall()

        cursor.execute("SELECT id as value, label FROM eea_spatialresolution ORDER BY id::int")
        spatial_resolutions = cursor.fetchall()

        cursor.execute("""
            SELECT d.id as value, d.id || ' - ' || COALESCE(dobj.label, '') as label
            FROM documents d
            LEFT JOIN eea_documentobject dobj ON d.documentobject_id = dobj.id
            ORDER BY d.id
        """)
        documents = cursor.fetchall()

        # MRI_10 / MRI_11 — needed by the gridded result upload, not by the model
        # form itself, which is why they were missing.
        cursor.execute("SELECT id as value, notation as label "
                       "FROM eea_concentrations ORDER BY LOWER(notation)")
        units = cursor.fetchall()

        cursor.execute("SELECT id::varchar as value, "
                       "COALESCE(NULLIF(notation, ''), label) as label "
                       "FROM eea_observationvalidity ORDER BY id::int")
        validities = cursor.fetchall()

        return jsonify({
            'pollutants': pollutants,
            'aggregation_processes': aggregation_processes,
            'result_encodings': result_encodings,
            'method_applications': method_applications,
            'spatial_resolutions': spatial_resolutions,
            'documents': documents,
            'units': units,
            'validities': validities,
        })


def _validated(model):
    try:
        validate_identifier('ModelAssessmentMethodId', model.id)
    except IdentifierError as e:
        raise BadRequest(str(e))
    return model


@models_endpoint.route('/api/management/models/insert', methods=['POST'])
@jwt_required_with_management_claim()
def models_insert():
    model = _validated(ModelObjectiveEstimationModel(**request.json))
    with CursorFromPool() as cursor:
        cursor.execute("""
            INSERT INTO models (
                id, data_aggregation_process_id, assessment_method_name, pollutant_id,
                result_encoding_id, method_application_id, generic_mqi,
                data_quality_document_id, method_document_id
            ) VALUES (
                %(id)s, %(data_aggregation_process_id)s, %(assessment_method_name)s, %(pollutant_id)s,
                %(result_encoding_id)s, %(method_application_id)s, %(generic_mqi)s,
                %(data_quality_document_id)s, %(method_document_id)s
            )
        """, model)
        if cursor.rowcount == 0:
            raise BadRequest('Could not insert model ' + model.id)
    return jsonify({'msg': 'Model created successfully'})


@models_endpoint.route('/api/management/models/update', methods=['POST'])
@jwt_required_with_management_claim()
def models_update():
    model = _validated(ModelObjectiveEstimationModel(**request.json))
    with CursorFromPool() as cursor:
        cursor.execute("""
            UPDATE models
            SET data_aggregation_process_id = %(data_aggregation_process_id)s,
                assessment_method_name      = %(assessment_method_name)s,
                pollutant_id                = %(pollutant_id)s,
                result_encoding_id          = %(result_encoding_id)s,
                method_application_id       = %(method_application_id)s,
                generic_mqi                 = %(generic_mqi)s,
                data_quality_document_id    = %(data_quality_document_id)s,
                method_document_id          = %(method_document_id)s
            WHERE id = %(id)s
        """, model)
        if cursor.rowcount == 0:
            raise BadRequest('Could not update model ' + model.id)
    return jsonify({'msg': 'Model updated successfully'})


@models_endpoint.route('/api/management/models/delete', methods=['POST'])
@jwt_required_with_management_claim()
def models_delete():
    model = DeleteModel(**request.json)
    rows = Q.delete('models', model)
    if rows == 0:
        raise BadRequest('Could not delete models ' + ','.join(model.ids))
    return jsonify({'msg': 'Model deleted successfully'})


# ---------------------------------------------------------------------------
# Gridded result ingest (AQR3 MRI)
# ---------------------------------------------------------------------------

def _cells_from_geotiff(filepath, resolution):
    """Read a GeoTIFF into (X, Y, value) cells on the AQR3 grid.

    Same rasterio approach as the SR upload, but it keeps the pixel value
    (MRI_09 Value) rather than only the footprint, and reprojects from the
    raster's own CRS instead of assuming WGS84.

    Several pixels commonly fall into one grid cell when a fine raster is
    reported at a coarser resolution. AQR3 keys MRI on the cell, so those are
    averaged into a single row rather than colliding on the primary key.
    """
    from collections import defaultdict

    import numpy as np
    import rasterio
    from rasterio.transform import xy as raster_xy

    with rasterio.open(filepath) as src:
        band = src.read(1)
        mask = (band != src.nodata) if src.nodata is not None else np.ones(band.shape, bool)
        rows, cols = np.where(mask)
        if len(rows) == 0:
            return []
        if len(rows) > MAX_CELLS:
            raise BadRequest(
                f'{len(rows)} raster cells exceeds the {MAX_CELLS} limit for a single upload. '
                f'Report at a coarser spatial resolution or split the file.')
        xs, ys = raster_xy(src.transform, rows, cols)
        values = band[rows, cols]
        source_srid = src.crs.to_epsg() if src.crs else 4326

    cells = points_to_inspire_grid(list(zip(xs, ys)), resolution, source_srid=source_srid)
    order = {cell: i for i, cell in enumerate(cells)}

    buckets = defaultdict(list)
    for cell, value in zip(
            (to_inspire_grid(x, y, resolution, source_srid=source_srid) for x, y in zip(xs, ys)),
            values):
        buckets[cell].append(float(value))

    return [(x, y, sum(vs) / len(vs))
            for (x, y), vs in sorted(buckets.items(), key=lambda kv: order.get(kv[0], 0))]


@models_endpoint.route('/api/management/models/<model_id>/results', methods=['POST'])
@jwt_required_with_management_claim()
def upload_results(model_id):
    """Load gridded model results for one timestep.

    Accepts a GeoTIFF (values per pixel) and writes moe_result_inline rows on the
    EEA INSPIRE grid. Form fields: file, spatial_resolution, start, end,
    data_aggregation_process_id, pollutant_id, unit_id, validity_id.
    """
    if 'file' not in request.files:
        raise BadRequest("File form does not contain the key 'file'")

    form = request.form
    # Named before the model is built so a blank required field reports its own
    # name rather than a coercion error on an empty string.
    required = ('spatial_resolution', 'start', 'data_aggregation_process_id')
    missing = [k for k in required if not form.get(k)]
    if missing:
        raise BadRequest(f'Missing required field(s): {", ".join(missing)}')

    meta = ModelResultUploadModel(
        assessment_method_id=model_id,
        start_time=form['start'],
        end_time=form.get('end') or None,
        data_aggregation_process_id=form['data_aggregation_process_id'],
        pollutant_id=form.get('pollutant_id') or None,
        unit_id=form.get('unit_id') or None,
        validity_id=form.get('validity_id') or None,
        spatial_resolution=form.get('spatial_resolution'),
    )

    try:
        resolution = validate_resolution(meta.spatial_resolution)
    except GridError as e:
        raise BadRequest(str(e))

    upload = request.files['file']
    name = (upload.filename or '').lower()
    if not name.endswith(('.tif', '.tiff')):
        raise BadRequest('Only GeoTIFF (.tif/.tiff) is supported for gridded results')

    with CursorFromPool() as cursor:
        cursor.execute('SELECT 1 FROM models WHERE id = %s', (model_id,))
        if cursor.fetchone() is None:
            raise BadRequest(f'Unknown model {model_id}')

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, os.path.basename(name))
            upload.save(filepath)
            cells = _cells_from_geotiff(filepath, resolution)

        if not cells:
            return jsonify({'msg': 'No data cells found in the raster', 'cells': 0})

        params = {**meta.model_dump(exclude={'value'}), 'spatial_resolution': resolution}

        cursor.execute("""
            DELETE FROM moe_result_inline
            WHERE assessment_method_id = %(assessment_method_id)s
              AND start_time = %(start_time)s::timestamp
              AND data_aggregation_process_id = %(data_aggregation_process_id)s
        """, params)

        cursor.executemany("""
            INSERT INTO moe_result_inline (
                assessment_method_id, start_time, data_aggregation_process_id, x, y,
                pollutant_id, end_time, value, unit_id, validity_id,
                spatial_resolution, result_time
            ) VALUES (
                %(assessment_method_id)s, %(start_time)s::timestamp,
                %(data_aggregation_process_id)s, %(x)s, %(y)s,
                %(pollutant_id)s, %(end_time)s::timestamp, %(value)s,
                %(unit_id)s, %(validity_id)s, %(spatial_resolution)s, now()
            )
        """, [{**params, 'x': x, 'y': y, 'value': round(v, 2)} for x, y, v in cells])

    return jsonify({
        'msg': f'Stored {len(cells)} grid cell(s)',
        'cells': len(cells),
        'spatial_resolution': resolution,
        'srid': 3035,
    })


# ---------------------------------------------------------------------------
# External gridded results (AQR3 MRE)
#
# One row per timestep rather than per grid cell: MRE says "the values are in
# this GeoTIFF", which the reporting country uploads to Reportnet3 itself, so
# raven records the reference and never the raster.
#
# Composite primary key (assessment_method_id, start_time,
# data_aggregation_process_id), so these are child routes of a model rather than
# a Manager page — Q.delete's `where id in (...)` cannot address the key, and
# adding a surrogate id would let two rows differ by surrogate while colliding on
# the AQR3 key at export.
# ---------------------------------------------------------------------------

_MRE_VALUES = ('pollutant_id', 'end_time', 'unit_id', 'validity_id', 'spatial_resolution',
               'geotiff_attachment')


def _validated_external(model):
    try:
        validate_reference('MRE_11', model.geotiff_attachment)
    except AttachmentReferenceError as e:
        raise BadRequest(str(e))
    return model


def _model_exists(cursor, model_id):
    cursor.execute('SELECT 1 FROM models WHERE id = %s', (model_id,))
    if cursor.fetchone() is None:
        raise BadRequest(f'Unknown model {model_id}')


@models_endpoint.route('/api/management/models/<model_id>/external-results', methods=['GET'])
@jwt_required_with_management_claim()
def external_results(model_id):
    with CursorFromPool() as cursor:
        _model_exists(cursor, model_id)
        cursor.execute("""
            SELECT to_char(e.start_time, 'YYYY-MM-DD HH24:MI') AS start_time,
                   to_char(e.end_time,   'YYYY-MM-DD HH24:MI') AS end_time,
                   e.data_aggregation_process_id,
                   COALESCE(NULLIF(ap.notation, ''), ap.label) AS data_aggregation_process,
                   e.pollutant_id,
                   COALESCE(NULLIF(p.notation, ''), p.label) AS pollutant,
                   e.unit_id, u.notation AS unit,
                   e.validity_id,
                   e.spatial_resolution,
                   e.geotiff_attachment,
                   to_char(e.result_time, 'YYYY-MM-DD HH24:MI') AS result_time
            FROM moe_result_external e
            LEFT JOIN eea_aggregationprocess ap ON e.data_aggregation_process_id = ap.id
            LEFT JOIN eea_pollutants p          ON e.pollutant_id = p.id
            LEFT JOIN eea_concentrations u      ON e.unit_id = u.id
            WHERE e.assessment_method_id = %(model_id)s
            ORDER BY e.start_time DESC, e.data_aggregation_process_id
        """, {'model_id': model_id})
        return jsonify(cursor.fetchall())


@models_endpoint.route('/api/management/models/<model_id>/external-results/insert',
                       methods=['POST'])
@jwt_required_with_management_claim()
def external_results_insert(model_id):
    payload = dict(request.json or {}, assessment_method_id=model_id)
    model = _validated_external(ExternalResultModel(**payload))

    columns = ('assessment_method_id', 'start_time', 'data_aggregation_process_id') + _MRE_VALUES
    values = ', '.join(
        f'%({c})s::timestamp' if c in ('start_time', 'end_time') else f'%({c})s'
        for c in columns)
    with CursorFromPool() as cursor:
        _model_exists(cursor, model_id)
        cursor.execute(f"""
            INSERT INTO moe_result_external ({', '.join(columns)}, result_time)
            VALUES ({values}, now())
        """, model)
    return jsonify({'msg': 'External result created'}), 201


@models_endpoint.route('/api/management/models/<model_id>/external-results/update',
                       methods=['POST'])
@jwt_required_with_management_claim()
def external_results_update(model_id):
    """Update one row, identified by `key`, with the values in `values`.

    start_time and data_aggregation_process_id are both part of the key and
    editable, so the key travels separately: an UPDATE keyed on the new values
    would match nothing and leave the original row behind.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest('Body must be {key: {start_time, data_aggregation_process_id}, '
                         'values: {...}}')

    key = ExternalResultKey(**dict(body['key'], assessment_method_id=model_id))
    model = _validated_external(
        ExternalResultModel(**dict(body['values'], assessment_method_id=model_id)))

    assignments = ', '.join(
        ['start_time = %(new_start_time)s::timestamp',
         'data_aggregation_process_id = %(new_data_aggregation_process_id)s',
         'result_time = now()'] +
        [f'{c} = %({c})s::timestamp' if c == 'end_time' else f'{c} = %({c})s'
         for c in _MRE_VALUES])

    params = {c: model[c] for c in _MRE_VALUES}
    params.update(new_start_time=model.start_time,
                  new_data_aggregation_process_id=model.data_aggregation_process_id,
                  assessment_method_id=model_id,
                  start_time=key.start_time,
                  data_aggregation_process_id=key.data_aggregation_process_id)

    with CursorFromPool() as cursor:
        cursor.execute(f"""
            UPDATE moe_result_external
            SET {assignments}
            WHERE assessment_method_id = %(assessment_method_id)s
              AND start_time = %(start_time)s::timestamp
              AND data_aggregation_process_id = %(data_aggregation_process_id)s
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(f'No external result for {key.start_time} / '
                             f'{key.data_aggregation_process_id}')
    return jsonify({'msg': 'External result updated'})


@models_endpoint.route('/api/management/models/<model_id>/external-results/delete',
                       methods=['POST'])
@jwt_required_with_management_claim()
def external_results_delete(model_id):
    key = ExternalResultKey(**dict(request.json or {}, assessment_method_id=model_id))
    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM moe_result_external
            WHERE assessment_method_id = %(assessment_method_id)s
              AND start_time = %(start_time)s::timestamp
              AND data_aggregation_process_id = %(data_aggregation_process_id)s
        """, key)
        if cursor.rowcount == 0:
            raise BadRequest(f'No external result for {key.start_time} / '
                             f'{key.data_aggregation_process_id}')
    return jsonify({'msg': 'External result deleted'})
