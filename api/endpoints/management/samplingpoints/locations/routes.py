"""AQR3 SPL SamplingPointLocation CRUD.

`sampling_point_locations` records where a sampling point was during a given
period. AQR3 expects one row per period, so a relocation closes the current
period and opens a new one rather than overwriting the old coordinates — the
history is what lets a reported measurement be traced to where it was taken.

Not the generic Manager CRUD, for two reasons: the primary key is composite
(sampling_point_id, location_begin), which `Q.delete`'s `where id in (...)`
cannot address, and the rows belong to a parent sampling point rather than
standing alone.

Every attribute column is nullable. The SPL export COALESCEs each one down to the
operational value on sampling_points/stations, so an override row need only carry
what actually changed for that period.
"""
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from core.database import CursorFromPool
from core.jwt_ext_custom import jwt_required_with_management_claim
from core.query import Q

from .models import LocationKey, LocationModel

samplingpoints_locations_endpoint = Blueprint('samplingpoints_locations', __name__)

BASE = '/api/management/samplingpoints/locations'

# Column order shared by the SELECT, INSERT and UPDATE so the three cannot drift.
ATTRIBUTES = (
    'location_end', 'station_area_id', 'sampling_point_category_id', 'hotspot', 'supersite',
    'latitude', 'longitude', 'altitude', 'inlet_height', 'building_distance', 'kerb_distance',
    'emission_source_distance',
)


def _require_access(sampling_point_id):
    if not sampling_point_id:
        raise BadRequest('sampling_point_id is required')
    if Q.has_no_access(sampling_point_id):
        raise BadRequest('Access denied for sampling point')


def _assert_no_overlap(cursor, model, replacing=None):
    """Reject a period that overlaps another for the same sampling point.

    The table only constrains location_end > location_begin, so two overlapping
    periods are storable — and would make SPL report two different locations for
    the same instant, with no way to tell which is right. A NULL location_end
    means "still current", so it overlaps everything after its start.

    Rejected rather than silently closing the previous period: for reporting data
    an implicit edit to a row the user did not name is worse than being told to
    close it themselves.
    """
    cursor.execute("""
        SELECT to_char(location_begin, 'YYYY-MM-DD HH24:MI') AS location_begin,
               to_char(location_end,   'YYYY-MM-DD HH24:MI') AS location_end
        FROM sampling_point_locations
        WHERE sampling_point_id = %(sampling_point_id)s
          AND (%(replacing)s::timestamp IS NULL OR location_begin <> %(replacing)s::timestamp)
          AND %(location_begin)s::timestamp < COALESCE(location_end, 'infinity'::timestamp)
          AND location_begin < COALESCE(%(location_end)s::timestamp, 'infinity'::timestamp)
        ORDER BY location_begin
        LIMIT 1
    """, {'sampling_point_id': model.sampling_point_id,
          'location_begin': model.location_begin,
          'location_end': model.location_end,
          'replacing': replacing})
    clash = cursor.fetchone()
    if clash:
        raise BadRequest(
            f'This period overlaps an existing one starting {clash["location_begin"]} '
            f'and ending {clash["location_end"] or "(still current)"}. Close that period '
            f'first — AQR3 reports one location per period, so overlapping periods would '
            f'report two locations for the same time.')


@samplingpoints_locations_endpoint.route(BASE, methods=['GET'])
@jwt_required_with_management_claim()
def list_locations():
    """Every location period for one sampling point, newest first.

    Returns the fallback the export would use for each empty attribute, so the
    UI can show what a blank cell will actually report rather than just "empty".
    """
    sampling_point_id = request.args.get('sampling_point_id')
    _require_access(sampling_point_id)

    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT
                to_char(spl.location_begin, 'YYYY-MM-DD HH24:MI') AS location_begin,
                to_char(spl.location_end,   'YYYY-MM-DD HH24:MI') AS location_end,
                spl.station_area_id,
                COALESCE(NULLIF(ac.notation, ''), ac.label) AS station_area,
                spl.sampling_point_category_id,
                sc.label AS sampling_point_category,
                spl.hotspot, spl.supersite,
                spl.latitude, spl.longitude, spl.altitude,
                spl.inlet_height, spl.building_distance, spl.kerb_distance,
                spl.emission_source_distance
            FROM sampling_point_locations spl
            LEFT JOIN eea_areaclassifications ac ON spl.station_area_id = ac.id
            LEFT JOIN eea_spocategory sc ON spl.sampling_point_category_id = sc.id
            WHERE spl.sampling_point_id = %(sp_id)s
            ORDER BY spl.location_begin DESC
        """, {'sp_id': sampling_point_id})
        periods = cursor.fetchall()

        # What an empty override falls back to, per the SPL export's COALESCE.
        cursor.execute("""
            SELECT to_char(sp.from_time, 'YYYY-MM-DD HH24:MI') AS from_time,
                   to_char(sp.to_time,   'YYYY-MM-DD HH24:MI') AS to_time,
                   COALESCE(NULLIF(ac.notation, ''), ac.label) AS station_area,
                   sc.label AS sampling_point_category,
                   sp.hotspot, st.supersite,
                   st.latitude, st.longitude, st.altitude,
                   sp.inlet_height, sp.building_distance, sp.kerb_distance,
                   sp.emission_source_distance
            FROM sampling_points sp
            JOIN stations st ON sp.station_id = st.id
            LEFT JOIN eea_areaclassifications ac ON st.station_area_id = ac.id
            LEFT JOIN eea_spocategory sc ON sp.sampling_point_category_id = sc.id
            WHERE sp.id = %(sp_id)s
        """, {'sp_id': sampling_point_id})
        defaults = cursor.fetchone()

    return jsonify({'periods': periods, 'defaults': defaults})


@samplingpoints_locations_endpoint.route(f'{BASE}/lookups', methods=['GET'])
@jwt_required_with_management_claim()
def lookups():
    with CursorFromPool() as cursor:
        cursor.execute("""
            SELECT COALESCE(NULLIF(r.notation, ''), r.label) AS label, r.id AS value
            FROM eea_areaclassifications r ORDER BY LOWER(r.label)
        """)
        station_areas = cursor.fetchall()

        cursor.execute("""
            SELECT COALESCE(NULLIF(r.label, ''), r.notation) AS label, r.id AS value
            FROM eea_spocategory r ORDER BY LOWER(r.label)
        """)
        categories = cursor.fetchall()

    return jsonify({'station_areas': station_areas, 'categories': categories})


@samplingpoints_locations_endpoint.route(f'{BASE}/insert', methods=['POST'])
@jwt_required_with_management_claim()
def insert():
    model = LocationModel(**request.json)
    _require_access(model.sampling_point_id)

    columns = ', '.join(('sampling_point_id', 'location_begin') + ATTRIBUTES)
    values = ', '.join(['%(sampling_point_id)s', '%(location_begin)s::timestamp'] +
                       [f'%({c})s::timestamp' if c == 'location_end' else f'%({c})s'
                        for c in ATTRIBUTES])
    with CursorFromPool() as cursor:
        _assert_no_overlap(cursor, model)
        cursor.execute(f'INSERT INTO sampling_point_locations ({columns}) VALUES ({values})',
                       model)
    return jsonify({'msg': 'Location period created'}), 201


@samplingpoints_locations_endpoint.route(f'{BASE}/update', methods=['POST'])
@jwt_required_with_management_claim()
def update():
    """Update one period, identified by `key`, with the values in `values`.

    The key is sent separately because `location_begin` is part of it: shifting a
    period's start has to move the existing row, and an UPDATE keyed on the new
    value would match nothing while leaving the old row in place.
    """
    body = request.json or {}
    if 'key' not in body or 'values' not in body:
        raise BadRequest("Body must be {key: {sampling_point_id, location_begin}, values: {...}}")

    key = LocationKey(**body['key'])
    model = LocationModel(**body['values'])
    _require_access(key.sampling_point_id)

    if model.sampling_point_id != key.sampling_point_id:
        raise BadRequest('A location period cannot be moved to another sampling point')

    assignments = ', '.join(['location_begin = %(new_location_begin)s::timestamp'] +
                            [f'{c} = %({c})s::timestamp' if c == 'location_end'
                             else f'{c} = %({c})s' for c in ATTRIBUTES])
    params = {c: model[c] for c in ATTRIBUTES}
    params.update(new_location_begin=model.location_begin,
                  sampling_point_id=key.sampling_point_id,
                  location_begin=key.location_begin)

    with CursorFromPool() as cursor:
        _assert_no_overlap(cursor, model, replacing=key.location_begin)
        cursor.execute(f"""
            UPDATE sampling_point_locations
            SET {assignments}
            WHERE sampling_point_id = %(sampling_point_id)s
              AND location_begin = %(location_begin)s::timestamp
        """, params)
        if cursor.rowcount == 0:
            raise BadRequest(f'No location period starting {key.location_begin} '
                             f'for {key.sampling_point_id}')
    return jsonify({'msg': 'Location period updated'})


@samplingpoints_locations_endpoint.route(f'{BASE}/delete', methods=['POST'])
@jwt_required_with_management_claim()
def delete():
    key = LocationKey(**(request.json or {}))
    _require_access(key.sampling_point_id)

    with CursorFromPool() as cursor:
        cursor.execute("""
            DELETE FROM sampling_point_locations
            WHERE sampling_point_id = %(sampling_point_id)s
              AND location_begin = %(location_begin)s::timestamp
        """, key)
        if cursor.rowcount == 0:
            raise BadRequest(f'No location period starting {key.location_begin} '
                             f'for {key.sampling_point_id}')
    return jsonify({'msg': 'Location period deleted'})
