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

from .models import ModelObjectiveEstimationModel

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

        return jsonify({
            'pollutants': pollutants,
            'aggregation_processes': aggregation_processes,
            'result_encodings': result_encodings,
            'method_applications': method_applications,
            'spatial_resolutions': spatial_resolutions,
            'documents': documents,
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
    required = ('spatial_resolution', 'start', 'data_aggregation_process_id')
    missing = [k for k in required if not form.get(k)]
    if missing:
        raise BadRequest(f'Missing required field(s): {", ".join(missing)}')

    try:
        resolution = validate_resolution(form.get('spatial_resolution'))
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

        params = {
            'assessment_method_id': model_id,
            'start_time': form['start'],
            'end_time': form.get('end') or None,
            'data_aggregation_process_id': form['data_aggregation_process_id'],
            'pollutant_id': form.get('pollutant_id') or None,
            'unit_id': form.get('unit_id') or None,
            'validity_id': form.get('validity_id') or None,
            'spatial_resolution': resolution,
        }

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
