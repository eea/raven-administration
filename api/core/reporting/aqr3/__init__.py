"""AQR3 v5.02 Reportnet3 CSV reporting.

The registry in `spec.py` is the single source of truth for which tables exist,
what their columns are called, and how each value is formatted.
"""
from core.reporting.aqr3.spec import AQR3_TABLES, LEGACY_SLUGS, TableSpec, Column, resolve
from core.reporting.aqr3.context import ExportContext, build_context
from core.reporting.aqr3.writer import (build_csv, build_csv_for, build_zip, iter_csv,
                                        primed, stream_csv)

__all__ = [
    'AQR3_TABLES', 'LEGACY_SLUGS', 'TableSpec', 'Column', 'resolve',
    'ExportContext', 'build_context',
    'build_csv', 'build_csv_for', 'build_zip', 'iter_csv', 'primed', 'stream_csv',
]
