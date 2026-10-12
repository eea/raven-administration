from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.data.csv_import import csv_response, import_rows, read_csv_rows
from core.database import CursorFromPool
from core.reporting.aqr3.attachments import AttachmentReferenceError, validate_reference
from core.reporting.aqr3.grid import GridError, points_to_inspire_grid, validate_resolution
from .models import SpatialRepresentativenessModel, SrImportModel, DeleteModel
import io
import secrets
import tempfile
import os

sr_endpoint = Blueprint("spatialrepresentativeness", __name__)

# How many points the form is sent to draw. The area itself is never cut to this:
# parse stages every point in srs_upload_points and the save reads them from there.
PREVIEW_POINTS = 2_000

# Guards against a file too large to hold in a worker, before and after reading it.
# A whole country at 10 m is billions of cells.
MAX_CANDIDATE_CELLS = 5_000_000
MAX_UPLOAD_POINTS = 5_000_000

# What SrCrud.vue's file picker offers (its ACCEPT). Anything else used to fall
# through to geopandas and fail as a 500 with a GDAL message.
EXTENSIONS = ('.geojson', '.json', '.gpkg', '.shp', '.zip', '.parquet', '.geoparquet',
              '.tif', '.tiff')


class SpatialFileError(ValueError):
    """The uploaded file is the user's to fix: reported as a 400 with this message."""


def _parse_area(file, source_epsg=4326, spatial_resolution=None):
    """Read any supported spatial file into points in EPSG:3035, unsnapped.

    Returns (xs, ys, filled): numpy arrays, and whether polygons or lines were filled
    with cells of `spatial_resolution` (see _cells_covering). Points are kept as they
    are and a raster gives its pixel centres, whatever the resolution. Arrays rather
    than lists of tuples: a raster can have millions of pixels.
    """
    import geopandas as gpd
    import numpy as np
    import shapely
    from pyproj import Transformer

    filename = file.filename.lower()
    if not filename.endswith(EXTENSIONS):
        raise SpatialFileError(f'{file.filename} is not a supported spatial file. '
                               f'Upload one of: {", ".join(EXTENSIONS)}.')

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, file.filename)
        file.save(filepath)

        if filename.endswith(".tif") or filename.endswith(".tiff"):
            import rasterio
            from rasterio.transform import xy as raster_xy
            with rasterio.open(filepath) as src:
                data = src.read(1)
                mask = (data != src.nodata) if src.nodata is not None else np.ones(data.shape, bool)
                if int(mask.sum()) > MAX_UPLOAD_POINTS:
                    raise SpatialFileError(
                        f'{file.filename} has {int(mask.sum()):,} data pixels; the limit is '
                        f'{MAX_UPLOAD_POINTS:,}. Resample it to coarser pixels first.')
                rows_arr, cols_arr = np.where(mask)
                xs, ys = raster_xy(src.transform, rows_arr, cols_arr)
                raster_epsg = src.crs.to_epsg() if src.crs else source_epsg
            t = Transformer.from_crs(f"EPSG:{raster_epsg}", "EPSG:3035", always_xy=True)
            x_out, y_out = t.transform(np.asarray(xs, dtype=float), np.asarray(ys, dtype=float))
            return np.asarray(x_out), np.asarray(y_out), False

        if filename.endswith(".zip"):
            import zipfile
            try:
                with zipfile.ZipFile(filepath, "r") as z:
                    z.extractall(tmpdir)
            except zipfile.BadZipFile:
                raise SpatialFileError(f'{file.filename} is not a readable zip file.')
            # Anywhere in the zip: zipping a folder, as Windows' "Send to > Compressed
            # folder" does, puts the shapefile one level down.
            shp_files = sorted(os.path.join(root, f) for root, _, files in os.walk(tmpdir)
                               for f in files if f.lower().endswith(".shp"))
            if not shp_files:
                raise SpatialFileError(f'No shapefile (.shp) found in {file.filename}.')
            gdf = gpd.read_file(shp_files[0])
        elif filename.endswith(".parquet") or filename.endswith(".geoparquet"):
            gdf = gpd.read_parquet(filepath)
        elif filename.endswith(".shp"):
            os.environ["SHAPE_RESTORE_SHX"] = "YES"
            gdf = gpd.read_file(filepath)
        else:
            gdf = gpd.read_file(filepath)

    if gdf.crs is None:
        gdf = gdf.set_crs(f"EPSG:{source_epsg}")
    geoms = gdf.geometry.to_crs("EPSG:3035")
    geoms = geoms[geoms.notna() & ~geoms.is_empty]

    is_point = geoms.geom_type.isin(["Point", "MultiPoint"])
    coords = shapely.get_coordinates(geoms[is_point].values)
    xs, ys = coords[:, 0], coords[:, 1]

    filled = bool((~is_point).any())
    if filled:
        cx, cy = _cells_covering(geoms[~is_point], spatial_resolution)
        xs, ys = np.concatenate([xs, cx]), np.concatenate([ys, cy])
    if len(xs) > MAX_UPLOAD_POINTS:
        raise SpatialFileError(f'{file.filename} gives {len(xs):,} points; the limit is '
                               f'{MAX_UPLOAD_POINTS:,}.')
    return xs, ys, filled


def _cells_covering(shapes, spatial_resolution):
    """The INSPIRE grid cells an area covers, as their centres in EPSG:3035.

    An SR area is very often drawn as polygons, and it used to be reduced to each
    polygon's centroid -- a whole area saved as one cell. A polygon now takes every
    cell whose centre lies inside it (the usual rasterisation rule, so neighbouring
    polygons never both claim a cell), and a polygon too small to contain any centre
    still takes the cell holding a point inside it. A line takes every cell it
    crosses. Centres rather than corners, so the save snaps each back to its cell.
    """
    import numpy as np
    import shapely

    if spatial_resolution in (None, ""):
        raise SpatialFileError(
            "This file holds areas (polygons or lines), which are filled with grid cells "
            "of the record's size. Choose the Spatial Resolution first, then upload it.")
    try:
        res = validate_resolution(spatial_resolution)
    except GridError as e:
        raise SpatialFileError(str(e))

    polygonal = shapely.union_all([g for g in shapes if g.geom_type.endswith("Polygon")])
    linear = shapely.union_all([g for g in shapes if "LineString" in g.geom_type
                                or g.geom_type == "LinearRing"])

    minx, miny, maxx, maxy = shapes.total_bounds
    x0, y0 = np.floor(minx / res) * res, np.floor(miny / res) * res
    ncols = int(np.floor(maxx / res) * res - x0) // res + 1
    nrows = int(np.floor(maxy / res) * res - y0) // res + 1
    if ncols * nrows > MAX_CANDIDATE_CELLS:
        raise SpatialFileError(
            f"The area spans about {ncols * nrows:,} cells of {res} m; the limit is "
            f"{MAX_CANDIDATE_CELLS:,}. Choose a coarser Spatial Resolution.")

    xs, ys = np.meshgrid(x0 + res * np.arange(ncols), y0 + res * np.arange(nrows))
    xs, ys = xs.ravel(), ys.ravel()
    keep = np.zeros(xs.shape, dtype=bool)

    if not polygonal.is_empty:
        keep |= shapely.contains_xy(polygonal, xs + res / 2, ys + res / 2)
        for part in getattr(polygonal, "geoms", [polygonal]):
            p = part.representative_point()
            keep |= (xs == np.floor(p.x / res) * res) & (ys == np.floor(p.y / res) * res)
    if not linear.is_empty:
        boxes = shapely.box(xs, ys, xs + res, ys + res)
        keep |= shapely.intersects(boxes, linear)

    return xs[keep] + res / 2, ys[keep] + res / 2


def _to_wgs84(xs, ys):
    """EPSG:3035 arrays -> [{x, y}] in EPSG:4326, the shape the form draws."""
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)
    lng, lat = t.transform(xs, ys)
    return [{"x": float(x), "y": float(y)} for x, y in zip(lng, lat)]


@sr_endpoint.route("/api/management/spatialrepresentativeness/lookups", methods=["GET"])
@jwt_required_with_management_claim()
def get_lookups():
    with CursorFromPool() as cursor:
        # eea_srapplication: spo_sr / exc_sr
        cursor.execute("""
            SELECT COALESCE(NULLIF(r.notation, ''), r.label) as label, r.id as value
            FROM eea_srapplication r
            ORDER BY LOWER(r.label)
        """)
        applications = cursor.fetchall()

        # eea_spatialresolution: 10, 100, 1000, 10000
        cursor.execute("""
            SELECT COALESCE(NULLIF(r.notation, ''), r.label) as label, r.id as value
            FROM eea_spatialresolution r
            ORDER BY r.id::int
        """)
        spatialresolutions = cursor.fetchall()

        # SRS_05 eea_resultencoding: inline / external / zone
        cursor.execute("""
            SELECT COALESCE(NULLIF(r.notation, ''), r.label) as label, r.id as value
            FROM eea_resultencoding r
            ORDER BY LOWER(r.label)
        """)
        resultencodings = cursor.fetchall()

        # SRS_06 has no vocabulary: the guide cross-checks it against the
        # SamplingPoint and Model tables, so offer both rather than free text.
        cursor.execute("""
            SELECT id AS value, id || ' (sampling point)' AS label FROM sampling_points
            UNION ALL
            SELECT id AS value, id || ' (model)' AS label FROM models
            ORDER BY label
        """)
        assessmentmethods = cursor.fetchall()

    return jsonify({"applications": applications,
                    "spatialresolutions": spatialresolutions,
                    "resultencodings": resultencodings,
                    "assessmentmethods": assessmentmethods})


@sr_endpoint.route("/api/management/spatialrepresentativeness", methods=["GET"])
@jwt_required_with_management_claim()
def get_all():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                sr.id,
                sr.srs_application_id,
                sr.srs_application,
                sr.result_encoding_id,
                COALESCE(NULLIF(re.notation, ''), re.label) AS result_encoding,
                sr.representativeness_assessment_method_id,
                ext.geotiff_attachment,
                sr.created_at,
                COUNT(a.id) AS point_count
            FROM spatial_representativeness sr
            LEFT JOIN eea_resultencoding re ON sr.result_encoding_id = re.id
            LEFT JOIN srs_external ext ON ext.spatial_representativeness_id = sr.id
            LEFT JOIN srs_inline a ON a.spatial_representativeness_id = sr.id
            GROUP BY sr.id, sr.srs_application_id, sr.srs_application, sr.result_encoding_id,
                     re.notation, re.label, sr.representativeness_assessment_method_id,
                     ext.geotiff_attachment, sr.created_at
            ORDER BY LOWER(sr.id)
        """)
        return jsonify(cursor.fetchall())


def _sync_external(cursor, obj):
    """Keep srs_external in step with the SR's result encoding.

    srs_external is strictly 1:1 with spatial_representativeness, and which of the
    two representations applies is what result_encoding_id says. So an SR encoded
    as `external` gets (or keeps) its row, and one switched back to inline loses
    it — leaving a stale external row would make SRE export a GeoTIFF reference
    for an area that is reported as grid cells.
    """
    if (obj.result_encoding_id or '').lower() == 'external':
        try:
            validate_reference('SRE_04', obj.geotiff_attachment)
        except AttachmentReferenceError as e:
            raise BadRequest(str(e))
        cursor.execute("""
            INSERT INTO srs_external (spatial_representativeness_id, spatial_resolution,
                                      geotiff_attachment)
            VALUES (%(id)s, %(spatial_resolution)s, %(geotiff_attachment)s)
            ON CONFLICT (spatial_representativeness_id) DO UPDATE
               SET spatial_resolution = excluded.spatial_resolution,
                   geotiff_attachment = excluded.geotiff_attachment
        """, {'id': obj.id, 'spatial_resolution': obj.spatial_resolution,
              'geotiff_attachment': obj.geotiff_attachment})
    else:
        cursor.execute('DELETE FROM srs_external WHERE spatial_representativeness_id = %s',
                       (obj.id,))


def _insert_points(cursor, sr_id, points_4326, spatial_resolution):
    """Store points sent as JSON (the API's original shape) as AQR3 SRI grid cells.

    Reprojects to EPSG:3035 *and snaps to the resolution* — a cell reference that
    is merely reprojected does not line up with the EEA's own gridding, and
    AQR3 keys SRI on (CountryCode, SRSApplicationId, X, Y). Snapping collapses
    several source points onto one cell, so the returned count is cells written,
    not points supplied. The form no longer sends points; it sends an upload token.
    """
    cursor.execute("DELETE FROM srs_inline WHERE spatial_representativeness_id = %s", (sr_id,))
    if not points_4326:
        return 0

    cells = points_to_inspire_grid([(pt.x, pt.y) for pt in points_4326],
                                   spatial_resolution, source_srid=4326)
    resolution = validate_resolution(spatial_resolution)
    cursor.executemany("""
        INSERT INTO srs_inline (spatial_representativeness_id, x, y, spatial_resolution)
        VALUES (%s, %s, %s, %s)
    """, [(sr_id, x, y, resolution) for x, y in cells])
    return len(cells)


def _insert_upload(cursor, sr_id, token, res):
    """Replace an SR's cells with every point of a parsed upload, snapped in SQL.

    The same floor as core.reporting.aqr3.grid.snap, on points parse already put in
    EPSG:3035, so a file of any size is saved whole without passing through Python.
    """
    cursor.execute("SELECT filename, fill_resolution FROM srs_uploads WHERE token = %s",
                   (token,))
    upload = cursor.fetchone()
    if not upload:
        raise BadRequest("The uploaded file is no longer available (uploads are kept for "
                         "a day, and each is used once). Upload it again.")
    if upload["fill_resolution"] and upload["fill_resolution"] != res:
        raise BadRequest(
            f'{upload["filename"]} was filled with {upload["fill_resolution"]} m cells, but '
            f'the Spatial Resolution is {res} m. Upload the file again.')

    cursor.execute("DELETE FROM srs_inline WHERE spatial_representativeness_id = %s", (sr_id,))
    cursor.execute("""
        INSERT INTO srs_inline (spatial_representativeness_id, x, y, spatial_resolution)
        SELECT DISTINCT %(sr)s,
               (floor(x / %(res)s) * %(res)s)::bigint,
               (floor(y / %(res)s) * %(res)s)::bigint,
               %(res)s
        FROM srs_upload_points WHERE token = %(token)s
    """, {"sr": sr_id, "res": res, "token": token})
    count = cursor.rowcount
    cursor.execute("DELETE FROM srs_uploads WHERE token = %s", (token,))
    return count


def _resnap_cells(cursor, source_id, target_id, res):
    """Give `target_id` the cells of `source_id`, at resolution `res`.

    For Duplicate (a new record taking another's area) and for an edit that changes
    only the resolution. Coarser works -- each cell's centre lands in exactly one
    bigger cell. Finer cannot be derived from coarse cells, so the file is needed.
    """
    cursor.execute("""
        SELECT MAX(spatial_resolution) AS res FROM srs_inline
        WHERE spatial_representativeness_id = %s
    """, (source_id,))
    current = cursor.fetchone()["res"]
    if current is None:
        return 0
    if res < current:
        raise BadRequest(
            f'The area is stored as {current} m cells; {res} m cells cannot be made from '
            f'them. Upload the spatial file again to use a finer resolution.')
    # Every reference to srs_inline in one statement sees the same snapshot, so
    # source and target may be the same record.
    cursor.execute("""
        WITH source AS (
            SELECT x, y, spatial_resolution AS r FROM srs_inline
            WHERE spatial_representativeness_id = %(source)s
        ), cleared AS (
            DELETE FROM srs_inline WHERE spatial_representativeness_id = %(target)s
        )
        INSERT INTO srs_inline (spatial_representativeness_id, x, y, spatial_resolution)
        SELECT DISTINCT %(target)s,
               (floor((x + r / 2.0) / %(res)s) * %(res)s)::bigint,
               (floor((y + r / 2.0) / %(res)s) * %(res)s)::bigint,
               %(res)s
        FROM source
    """, {"source": source_id, "target": target_id, "res": res})
    return cursor.rowcount


def _store_area(cursor, obj, editing=False):
    """Write the record's grid cells from whichever source the request names.

    In order: a parsed upload (the form), points as JSON (the original API shape),
    another record's cells (Duplicate). An edit naming none of them keeps its cells,
    re-snapped if only the resolution changed. Returns the record's cell count.
    """
    def resolution():
        try:
            return validate_resolution(obj.spatial_resolution)
        except GridError as e:
            raise BadRequest(str(e))

    if obj.upload_token:
        return _insert_upload(cursor, obj.id, obj.upload_token, resolution())
    if obj.points:
        return _insert_points(cursor, obj.id, obj.points, resolution())
    if obj.copy_cells_from:
        return _resnap_cells(cursor, obj.copy_cells_from, obj.id, resolution())
    if editing and obj.spatial_resolution:
        cursor.execute("""
            SELECT COUNT(*) AS n, MIN(spatial_resolution) AS lo, MAX(spatial_resolution) AS hi
            FROM srs_inline WHERE spatial_representativeness_id = %s
        """, (obj.id,))
        stored = cursor.fetchone()
        res = resolution()
        if stored["n"] and (stored["lo"] != res or stored["hi"] != res):
            return _resnap_cells(cursor, obj.id, obj.id, res)
        return stored["n"]
    return 0


def _save(cursor, obj):
    """Insert one SR with its area. The form's insert and the CSV import both write
    through here; an import carries no area, so it is added in the form."""
    cursor.execute("""
        INSERT INTO spatial_representativeness
            (id, srs_application_id, srs_application, result_encoding_id,
             representativeness_assessment_method_id)
        VALUES (%(id)s, %(srs_application_id)s, %(srs_application)s, %(result_encoding_id)s,
                %(representativeness_assessment_method_id)s)
    """, {"id": obj.id, "srs_application_id": obj.srs_application_id,
          "srs_application": obj.srs_application,
          "result_encoding_id": obj.result_encoding_id,
          "representativeness_assessment_method_id":
              obj.representativeness_assessment_method_id})
    _sync_external(cursor, obj)
    return _store_area(cursor, obj)


@sr_endpoint.route("/api/management/spatialrepresentativeness/insert", methods=["POST"])
@jwt_required_with_management_claim()
def insert():
    obj = SpatialRepresentativenessModel(**request.json)
    with CursorFromPool() as cursor:
        count = _save(cursor, obj)
    return {"message": "Inserted", "id": obj.id, "point_count": count}, 201


@sr_endpoint.route("/api/management/spatialrepresentativeness/import", methods=["POST"])
@jwt_required_with_management_claim()
def import_csv():
    """One SR per CSV row, without its area: the grid cells come from a spatial file
    in the form, which a CSV row cannot carry."""
    if "file" not in request.files:
        raise BadRequest("File form does not contain the key 'file'")
    rows = read_csv_rows(request.files["file"], SrImportModel)
    with CursorFromPool() as cursor:
        count = import_rows(cursor, rows, SrImportModel, _save)
    return jsonify({"msg": f"{count} spatial representativeness record(s) imported"})


@sr_endpoint.route("/api/management/spatialrepresentativeness/export", methods=["GET"])
@jwt_required_with_management_claim()
def export_csv():
    """The columns the import takes, so the file is also its template. The area is
    not in it; spatial_resolution is the external GeoTIFF's, or else the grid's."""
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT sr.id, sr.srs_application_id, sr.srs_application,
                   sr.result_encoding_id, sr.representativeness_assessment_method_id,
                   COALESCE(ext.spatial_resolution,
                            (SELECT MIN(a.spatial_resolution) FROM srs_inline a
                              WHERE a.spatial_representativeness_id = sr.id)) AS spatial_resolution,
                   ext.geotiff_attachment
            FROM spatial_representativeness sr
            LEFT JOIN srs_external ext ON ext.spatial_representativeness_id = sr.id
            ORDER BY LOWER(sr.id)
        """)
        return csv_response(cursor.fetchall(), SrImportModel,
                            "spatial_representativeness.csv")


@sr_endpoint.route("/api/management/spatialrepresentativeness/update", methods=["POST"])
@jwt_required_with_management_claim()
def update():
    obj = SpatialRepresentativenessModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            UPDATE spatial_representativeness
            SET srs_application_id = %(srs_application_id)s,
                srs_application = %(srs_application)s,
                result_encoding_id = %(result_encoding_id)s,
                representativeness_assessment_method_id =
                    %(representativeness_assessment_method_id)s
            WHERE id = %(id)s
        """, {"id": obj.id, "srs_application_id": obj.srs_application_id,
              "srs_application": obj.srs_application,
              "result_encoding_id": obj.result_encoding_id,
              "representativeness_assessment_method_id":
                  obj.representativeness_assessment_method_id})
        if cursor.rowcount == 0:
            return {"error": "Not found"}, 404
        _sync_external(cursor, obj)
        count = _store_area(cursor, obj, editing=True)
    return {"message": "Updated", "point_count": count}, 200


@sr_endpoint.route("/api/management/spatialrepresentativeness/delete", methods=["POST"])
@jwt_required_with_management_claim()
def delete():
    dm = DeleteModel(**request.json)
    ids = tuple(dm.ids)
    placeholders = ",".join(["%s"] * len(ids))
    with CursorFromPool() as cursor:
        cursor.execute(f"DELETE FROM spatial_representativeness WHERE id IN ({placeholders})", ids)
        if cursor.rowcount == 0:
            return {"error": "Not found"}, 404
    return {"message": f"Deleted {cursor.rowcount} record(s)"}, 200


@sr_endpoint.route("/api/management/spatialrepresentativeness/<sr_id>", methods=["GET"])
@jwt_required_with_management_claim()
def get_by_id(sr_id):
    """The record, its cell count, and up to PREVIEW_POINTS of its cells to draw.

    Only a sample: an area can have millions of cells, and the form no longer sends
    them back -- an edit keeps the stored cells, a Duplicate copies them server-side.
    """
    import numpy as np
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT sr.id, sr.srs_application_id, sr.srs_application, sr.created_at,
                   sr.result_encoding_id, sr.representativeness_assessment_method_id,
                   ext.geotiff_attachment, ext.spatial_resolution AS external_resolution,
                   (SELECT COUNT(*) FROM srs_inline a
                     WHERE a.spatial_representativeness_id = sr.id) AS point_count,
                   (SELECT MIN(a.spatial_resolution) FROM srs_inline a
                     WHERE a.spatial_representativeness_id = sr.id) AS cell_resolution
            FROM spatial_representativeness sr
            LEFT JOIN srs_external ext ON ext.spatial_representativeness_id = sr.id
            WHERE sr.id = %s
        """, (sr_id,))
        record = cursor.fetchone()
        if not record:
            return {"error": "Not found"}, 404

        # Every n-th cell, so the sample covers the whole area.
        step = max(1, -(-record["point_count"] // PREVIEW_POINTS))
        cursor.execute("""
            SELECT x, y, spatial_resolution FROM (
                SELECT x, y, spatial_resolution, row_number() OVER (ORDER BY id) AS n
                FROM srs_inline WHERE spatial_representativeness_id = %s
            ) cells WHERE (n - 1) %% %s = 0
        """, (sr_id, step))
        cells = cursor.fetchall()

    # Cell centres, not the stored lower-left corners: a corner sits on four cells.
    points = []
    if cells:
        half = np.array([(c["spatial_resolution"] or 0) / 2 for c in cells], dtype=float)
        points = _to_wgs84(np.array([c["x"] for c in cells], dtype=float) + half,
                           np.array([c["y"] for c in cells], dtype=float) + half)

    return jsonify({
        "id":                 record["id"],
        "srs_application_id": record["srs_application_id"],
        "srs_application":    record["srs_application"],
        "result_encoding_id": record["result_encoding_id"],
        "representativeness_assessment_method_id":
            record["representativeness_assessment_method_id"],
        "geotiff_attachment": record["geotiff_attachment"],
        "created_at":         str(record["created_at"]) if record["created_at"] else None,
        # With no cells there is no per-cell resolution to read; fall back to the
        # external GeoTIFF's.
        "spatial_resolution": record["cell_resolution"] or record["external_resolution"],
        "point_count":        record["point_count"],
        "points":             points,
        "sampled":            len(points) < record["point_count"],
    })


@sr_endpoint.route("/api/management/spatialrepresentativeness/parse", methods=["POST"])
@jwt_required_with_management_claim()
def parse_file():
    """Read a spatial file, stage all its points, and return a token and a preview.

    The save sends the token (upload_token) rather than the points, so the area is
    saved whole however large it is. This used to return at most 50,000 points, and
    the form saved exactly those.
    """
    import numpy as np
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    file = request.files["file"]
    try:
        source_epsg = int(request.form.get("source_epsg", 4326))
    except ValueError:
        return {"error": f'source_epsg must be an EPSG code, got {request.form.get("source_epsg")!r}'}, 400
    resolution = request.form.get("spatial_resolution") or None
    try:
        xs, ys, filled = _parse_area(file, source_epsg, resolution)
    except SpatialFileError as e:
        return {"error": str(e)}, 400
    except Exception as e:
        # Every reader (pyogrio, pyarrow, rasterio) raises its own type for a file it
        # cannot read, and an unreadable upload is the user's to fix, not a server
        # fault. Say which file, and keep the reader's reason.
        return {"error": f"Could not read {file.filename} as a spatial file: {e}"}, 400

    token = secrets.token_hex(16)
    with CursorFromPool() as cursor:
        # Files picked and never saved.
        cursor.execute("DELETE FROM srs_uploads WHERE uploaded_at < now() - interval '1 day'")
        cursor.execute("""
            INSERT INTO srs_uploads (token, filename, point_count, fill_resolution)
            VALUES (%s, %s, %s, %s)
        """, (token, file.filename[:255], len(xs),
              validate_resolution(resolution) if filled else None))
        # COPY in chunks: millions of rows, without one string holding them all.
        for start in range(0, len(xs), 500_000):
            buf = io.StringIO()
            np.savetxt(buf, np.column_stack([xs[start:start + 500_000],
                                             ys[start:start + 500_000]]),
                       fmt=token + "\t%.3f\t%.3f")
            buf.seek(0)
            cursor.copy_expert("COPY srs_upload_points (token, x, y) FROM STDIN", buf)

    pick = np.unique(np.linspace(0, len(xs) - 1, min(len(xs), PREVIEW_POINTS)).astype(int))
    return jsonify({
        "upload_token": token,
        "points": _to_wgs84(xs[pick], ys[pick]) if len(xs) else [],
        "total": int(len(xs)),
        # The preview is a sample; the saved area is not.
        "truncated": len(pick) < len(xs),
    })
