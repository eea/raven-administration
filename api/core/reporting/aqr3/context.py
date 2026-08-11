"""Per-export context: the values every AQR3 table needs.

Resolved once per request rather than per table. The previous export layer
re-queried the single-row `settings` table in each of its eight route handlers.
"""
from dataclasses import dataclass
from typing import Optional

from core.eea.id_generator import get_country_code_from_settings


@dataclass(frozen=True)
class ExportContext:
    """Country code, reporting timezone offset and (optionally) reporting year."""
    country_code: Optional[str]
    timezone_offset: str
    year: Optional[int] = None

    def with_year(self, year):
        return ExportContext(self.country_code, self.timezone_offset, year)


def build_context(cursor, year=None):
    """Read settings once and resolve the reporting timezone offset."""
    country_code = get_country_code_from_settings(cursor)

    cursor.execute("""
        SELECT tz.timezone_offset
        FROM settings s
        LEFT JOIN eea_timezones tz ON s.timezone_id = tz.id
        LIMIT 1
    """)
    row = cursor.fetchone()
    offset = (row['timezone_offset'] if row and row['timezone_offset'] else '') if row else ''

    return ExportContext(country_code=country_code, timezone_offset=offset, year=year)
