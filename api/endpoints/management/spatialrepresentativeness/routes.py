from flask import Blueprint, request, jsonify
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.database import CursorFromPool
from .models import SpatialRepresentativenessModel, DeleteModel
import io
import tempfile
import os

sr_endpoint = Blueprint("spatialrepresentativeness", __name__)

MAX_POINTS = 50_000


def _parse_to_wgs84(file, source_epsg=4326):
    """Parse any supported spatial file; return list of (x, y) tuples in EPSG:4326."""
    import geopandas as gpd
    import numpy as np
    from pyproj import Transformer

    filename = file.filename.lower()

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, file.filename)
        file.save(filepath)

        if filename.endswith(".tif") or filename.endswith(".tiff"):
            import rasterio
            from rasterio.transform import xy as raster_xy
            with rasterio.open(filepath) as src:
                data = src.read(1)
                mask = (data != src.nodata) if src.nodata is not None else np.ones(data.shape, bool)
                rows_arr, cols_arr = np.where(mask)
                xs, ys = raster_xy(src.transform, rows_arr, cols_arr)
                raster_epsg = src.crs.to_epsg() if src.crs else source_epsg
            t = Transformer.from_crs(f"EPSG:{raster_epsg}", "EPSG:4326", always_xy=True)
            x_out, y_out = t.transform(xs, ys)
            return [(float(x), float(y)) for x, y in zip(x_out, y_out)]

        if filename.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(filepath, "r") as z:
                z.extractall(tmpdir)
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
            if not shp_files:
                raise ValueError("No .shp found in zip")
            gdf = gpd.read_file(os.path.join(tmpdir, shp_files[0]))
        elif filename.endswith(".parquet") or filename.endswith(".geoparquet"):
            gdf = gpd.read_parquet(filepath)
        elif filename.endswith(".shp"):
            import os as _os
            _os.environ["SHAPE_RESTORE_SHX"] = "YES"
            gdf = gpd.read_file(filepath)
        else:
            gdf = gpd.read_file(filepath)

        if gdf.crs is None:
            gdf = gdf.set_crs(f"EPSG:{source_epsg}")
        if str(gdf.crs.to_epsg()) != "4326":
            gdf = gdf.to_crs("EPSG:4326")

        points = []
        for geom in gdf.geometry:
            if geom is None:
                continue
            pt = geom if geom.geom_type == "Point" else geom.centroid
            points.append((float(pt.x), float(pt.y)))

        return points


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

    return jsonify({"applications": applications, "spatialresolutions": spatialresolutions})


@sr_endpoint.route("/api/management/spatialrepresentativeness", methods=["GET"])
@jwt_required_with_management_claim()
def get_all():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                sr.id,
                sr.sr_application_id,
                sr.application,
                sr.created_at,
                COUNT(a.id) AS point_count
            FROM spatial_representativeness sr
            LEFT JOIN sr_area_inline a ON a.spatial_representativeness_id = sr.id
            GROUP BY sr.id, sr.sr_application_id, sr.application, sr.created_at
            ORDER BY LOWER(sr.id)
        """)
        return jsonify(cursor.fetchall())


def _insert_points(cursor, sr_id, points_4326, spatial_resolution):
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    cursor.execute("DELETE FROM sr_area_inline WHERE spatial_representativeness_id = %s", (sr_id,))
    if points_4326:
        args = []
        for pt in points_4326:
            x_3035, y_3035 = t.transform(pt.x, pt.y)
            args.append((sr_id, float(x_3035), float(y_3035), spatial_resolution or None))
        cursor.executemany("""
            INSERT INTO sr_area_inline (spatial_representativeness_id, x, y, spatial_resolution)
            VALUES (%s, %s, %s, %s)
        """, args)
    return len(points_4326)


@sr_endpoint.route("/api/management/spatialrepresentativeness/insert", methods=["POST"])
@jwt_required_with_management_claim()
def insert():
    obj = SpatialRepresentativenessModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            INSERT INTO spatial_representativeness (id, sr_application_id, application)
            VALUES (%(id)s, %(sr_application_id)s, %(application)s)
        """, {"id": obj.id, "sr_application_id": obj.sr_application_id, "application": obj.application})
        count = _insert_points(cursor, obj.id, obj.points, obj.spatial_resolution)
    return {"message": "Inserted", "id": obj.id, "point_count": count}, 201


@sr_endpoint.route("/api/management/spatialrepresentativeness/update", methods=["POST"])
@jwt_required_with_management_claim()
def update():
    obj = SpatialRepresentativenessModel(**request.json)
    with CursorFromPool() as cursor:
        cursor.execute("""
            UPDATE spatial_representativeness
            SET sr_application_id = %(sr_application_id)s,
                application = %(application)s
            WHERE id = %(id)s
        """, {"id": obj.id, "sr_application_id": obj.sr_application_id, "application": obj.application})
        if cursor.rowcount == 0:
            return {"error": "Not found"}, 404
        if obj.points:
            _insert_points(cursor, obj.id, obj.points, obj.spatial_resolution)
    return {"message": "Updated"}, 200


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
    """Return SR record with points in EPSG:4326 — same shape as insert/update."""
    from pyproj import Transformer
    t = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT sr.id, sr.sr_application_id, sr.application, sr.created_at,
                   a.x, a.y, a.spatial_resolution
            FROM spatial_representativeness sr
            LEFT JOIN sr_area_inline a ON a.spatial_representativeness_id = sr.id
            WHERE sr.id = %s
            ORDER BY a.id
        """, (sr_id,))
        rows = cursor.fetchall()

    if not rows:
        return {"error": "Not found"}, 404

    first = rows[0]
    points = []
    spatial_resolution = None
    for row in rows:
        if row["x"] is not None:
            lng, lat = t.transform(row["x"], row["y"])
            points.append({"x": float(lng), "y": float(lat)})
            if spatial_resolution is None:
                spatial_resolution = row["spatial_resolution"]

    return jsonify({
        "id":                 first["id"],
        "sr_application_id":  first["sr_application_id"],
        "application":        first["application"],
        "created_at":         str(first["created_at"]) if first["created_at"] else None,
        "spatial_resolution": spatial_resolution,
        "points":             points
    })


@sr_endpoint.route("/api/management/spatialrepresentativeness/parse", methods=["POST"])
@jwt_required_with_management_claim()
def parse_file():
    """Parse a spatial file and return points in EPSG:4326 for preview (no DB write)."""
    if "file" not in request.files:
        return {"error": "No file provided"}, 400
    file = request.files["file"]
    source_epsg = int(request.form.get("source_epsg", 4326))
    try:
        points = _parse_to_wgs84(file, source_epsg)
        truncated = len(points) > MAX_POINTS
        preview = points[:MAX_POINTS]
        return jsonify({
            "points": [{"x": x, "y": y} for x, y in preview],
            "total": len(points),
            "truncated": truncated
        })
    except Exception as e:
        return {"error": str(e)}, 500
