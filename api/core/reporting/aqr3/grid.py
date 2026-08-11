"""The EEA INSPIRE common grid.

AQR3 v5.02 maintains spatial coherence through a single grid (guide,
Introduction sheet): the EEA INSPIRE grid in Europe LAEA, **EPSG:3035**, at
resolution steps of 10, 100, 1000 or 10000 m. It applies to sampling point
locations, zone geometries, exceedance extents, modelling results and spatial
representativeness areas alike.

Reprojecting is only half the job — a cell reference must also be *snapped* to
the resolution, otherwise two sources describing the same cell disagree and the
EEA's cross-checks fail. The existing SR ingest reprojected to 3035 but stored
raw floats, so this centralises both steps.
"""
from functools import lru_cache

ALLOWED_RESOLUTIONS = (10, 100, 1000, 10000)
INSPIRE_SRID = 3035


class GridError(ValueError):
    """An unusable resolution or coordinate."""


def validate_resolution(resolution):
    """Coerce to one of the AQR3 resolution steps."""
    if resolution is None:
        raise GridError(
            f'A spatial resolution is required; AQR3 allows {ALLOWED_RESOLUTIONS} metres')
    try:
        value = int(resolution)
    except (TypeError, ValueError):
        raise GridError(f'Spatial resolution {resolution!r} is not an integer number of metres')
    if value not in ALLOWED_RESOLUTIONS:
        raise GridError(
            f'Spatial resolution {value} m is not an AQR3 grid step; '
            f'allowed: {", ".join(str(r) for r in ALLOWED_RESOLUTIONS)}')
    return value


@lru_cache(maxsize=8)
def _transformer(source_srid):
    """Cached pyproj transformer. Building one per point is very slow."""
    from pyproj import Transformer
    return Transformer.from_crs(f'EPSG:{source_srid}', f'EPSG:{INSPIRE_SRID}',
                                always_xy=True)


def snap(x, y, resolution):
    """Snap an EPSG:3035 coordinate to the lower-left corner of its grid cell.

    Lower-left (floor) rather than nearest: the INSPIRE grid identifies a cell by
    its origin, so flooring is what makes two sources agree on the same cell.
    """
    res = validate_resolution(resolution)
    return (int(x // res) * res, int(y // res) * res)


def to_inspire_grid(x, y, resolution, source_srid=4326):
    """Reproject to EPSG:3035 and snap to the grid. Returns (X, Y) integers."""
    res = validate_resolution(resolution)
    if source_srid == INSPIRE_SRID:
        return snap(x, y, res)
    east, north = _transformer(source_srid).transform(x, y)
    return snap(east, north, res)


def points_to_inspire_grid(points, resolution, source_srid=4326):
    """Convert many (x, y) pairs, de-duplicated.

    Several source points commonly fall in one cell — especially when a fine
    raster is reported at a coarse resolution — and AQR3 keys MRI and SRI on the
    cell, so duplicates would violate the primary key.
    """
    res = validate_resolution(resolution)
    if not points:
        return []

    if source_srid == INSPIRE_SRID:
        cells = {snap(x, y, res) for x, y in points}
    else:
        transformer = _transformer(source_srid)
        xs, ys = zip(*points)
        easts, norths = transformer.transform(xs, ys)
        cells = {snap(e, n, res) for e, n in zip(easts, norths)}

    return sorted(cells)
