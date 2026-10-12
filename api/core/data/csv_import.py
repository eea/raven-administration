"""CSV import that saves each row the way the page's form does.

The generic importer (core/data/management.py) writes rows straight into a table,
so a page whose insert route carries rules of its own -- a derived id, an
exactly-one-of check, a per-attainment uniqueness the database cannot express --
would accept through import what its form refuses. Pages like that import through
here instead: every row is validated by the page's pydantic model and written by
the same function its insert route calls.

All rows go through one cursor, so a file is saved whole or not at all:
CursorFromPool rolls the transaction back on the first exception.
"""
import io

import pandas as pd
import psycopg2
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException

# What an empty cell may be written as. Shared with the generic importer, so a file
# that imports on one page reads the same on another.
NA_VALUES = ['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a',
             '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan']


def columns(model_cls):
    """The CSV header for a model: its fields, less any marked `exclude=True`."""
    return [name for name, f in model_cls.model_fields.items() if not f.exclude]


def read_csv_rows(file, model_cls):
    """The rows of an uploaded CSV, as dicts keyed by the model's field names.

    Every value is read as text and left to the model to convert. Letting pandas
    infer types would turn an id such as 007 into the number 7, and a whole-number
    column with an empty cell into floats.
    """
    if not (file.filename or '').lower().endswith('.csv'):
        raise BadRequest(f'File type is not supported: {file.filename}. Upload a .csv file.')

    accepted = columns(model_cls)
    try:
        df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8-sig')), dtype=str,
                         skipinitialspace=True, keep_default_na=False, na_values=NA_VALUES)
    except UnicodeDecodeError:
        raise BadRequest('The file is not UTF-8 encoded. Save it as CSV UTF-8 and try again.')
    except pd.errors.EmptyDataError:
        raise BadRequest(f'The file is empty. Expected the columns: {", ".join(accepted)}.')

    df.columns = [str(c).strip() for c in df.columns]
    unknown = [c for c in df.columns if c not in accepted]
    if unknown:
        raise BadRequest(f'Unknown column(s): {", ".join(unknown)}. '
                         f'Accepted columns: {", ".join(accepted)}.')
    missing = [name for name in accepted
               if model_cls.model_fields[name].is_required() and name not in df.columns]
    if missing:
        raise BadRequest(f'Missing column(s): {", ".join(missing)}. '
                         f'Accepted columns: {", ".join(accepted)}.')
    if df.empty:
        raise BadRequest('The file has a header but no rows.')

    df = df.astype(object).where(pd.notnull(df), None)
    return df.to_dict('records')


def _pydantic_message(e):
    first = e.errors()[0] if e.errors() else {}
    field = ' -> '.join(str(loc) for loc in first.get('loc', []))
    message = first.get('msg', 'Validation error')
    return f'{field}: {message}' if field else message


def import_rows(cursor, rows, model_cls, save):
    """Validate and save each row with `save(cursor, model)`; return the count.

    A failure is reported with its CSV line number (the header is line 1), and the
    exception propagates, so the caller's CursorFromPool rolls back the whole file.
    """
    for index, row in enumerate(rows):
        line = index + 2
        try:
            save(cursor, model_cls(**row))
        except ValidationError as e:
            raise BadRequest(f'Row {line}: {_pydantic_message(e)}') from e
        except HTTPException as e:
            raise BadRequest(f'Row {line}: {e.description}') from e
        except psycopg2.Error as e:
            # A broken reference or a duplicate key: the caller's data, not a fault.
            detail = (e.diag.message_detail or e.diag.message_primary
                      if e.diag else None) or str(e).strip()
            raise BadRequest(f'Row {line}: {detail}') from e
    return len(rows)


def csv_response(rows, model_cls, name):
    """`rows` as a CSV whose header is exactly what read_csv_rows accepts.

    The header is written even for an empty table, so the download doubles as a
    template, and exporting then importing gives back the same rows.
    """
    from core.utils import U
    # object, so a whole-number column with an empty cell stays 7 rather than 7.0,
    # which the model would refuse on the way back in.
    df = pd.DataFrame(rows, columns=columns(model_cls), dtype=object)
    return U.dataframe_to_csv_response(df, name)
