"""Value formatting for AQR3 v5.02 CSV output.

AQR3 has a small fixed set of value rules applied identically across all 17
tables. They live here so a fix lands once rather than in every table's row
builder.

Two rules are easy to get wrong and worth stating explicitly:

  * Empty means NULL, and only NULL. `0` is a legitimate BuildingDistance and
    `false` a legitimate Hotspot, so nothing here may use a falsy test.
  * Numerics are quantised to the scale the spec declares, not to whatever the
    database happens to store. Latitude is decimal(8,4) in AQR3 but
    numeric(10,7) in `stations`; emitting 7 decimals overruns the declared scale.
"""
import json


def text(value):
    """Plain string. NULL -> empty."""
    return '' if value is None else str(value)


def integer(value):
    """AQR3 numeric with no decimals (PollutantId, X, Y, years, resolutions)."""
    if value is None:
        return ''
    return str(int(value))


def decimals(dp):
    """Build a formatter quantising to `dp` decimal places.

    Mirrors the scale of the spec's SQL type, e.g. decimal(8,4) -> decimals(4).
    """
    def fmt(value):
        if value is None:
            return ''
        return f'{float(value):.{dp}f}'
    fmt.__name__ = f'decimals{dp}'
    return fmt


def boolean(value):
    """AQR3 bit/boolean as lowercase true/false."""
    if value is None:
        return ''
    return 'true' if value else 'false'


def datetime_with(offset):
    """Build a datetime formatter appending the reporting timezone offset.

    AQR3 datetimes are 'YYYY-MM-DD HH:MM:SS' plus the offset of the timezone the
    country reports in (eea_timezones.timezone_offset, e.g. '+01:00' or 'Z').
    """
    def fmt(value):
        if value is None:
            return ''
        stamp = value.strftime('%Y-%m-%d %H:%M:%S')
        return f'{stamp}{offset}' if offset else stamp
    fmt.__name__ = 'datetime'
    return fmt


def geojson_feature(value):
    """Wrap a PostGIS GeoJSON geometry as a Feature carrying its SRID.

    ZGE_03 ZoneGeometryGeoJson expects a Feature, not a bare geometry, and the
    EEA examples carry the SRID as a property.
    """
    if value is None:
        return ''
    return json.dumps(
        {'type': 'Feature', 'geometry': value, 'properties': {'srid': '4326'}},
        separators=(',', ':'))


# Convenience aliases matching the scales AQR3 actually uses.
coordinate = decimals(4)   # decimal(8,4)  — Latitude, Longitude
metres = decimals(1)       # decimal(10,1) — Altitude, InletHeight, distances
percent = decimals(2)      # decimal(5,2)  — DataCoverage, MQI, DataCapture
concentration = decimals(2)  # decimal(10,2) — Value, Contribution
level = decimals(3)        # decimal(10,3) — PollutionLevel
