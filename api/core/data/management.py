import pandas as pd
from pandas import DataFrame
import geopandas as gp
import io
from shapely import wkt
from werkzeug.exceptions import BadRequest


# ---------------------------------------------------------------------------
# Generic import/export CSV header contract
#
# This class derives its CSV headers straight from information_schema, so the
# headers *are* the database column names. The AQR3 v5.02 rename therefore
# changed the /api/exports/* and /api/imports/* contracts for every table at
# once, which would silently break external callers and the checked-in
# csv_examples/.
#
# So v1 is frozen: `naming='v1'` (the default) translates between the legacy
# header and the current column on the way out and back in. `naming='v2'` uses
# the AQR3-aligned column names and is served under /api/v2/*.
#
# Only columns that were actually renamed appear here.
# ---------------------------------------------------------------------------
V1_ALIASES = {
    'authorities': {
        'organisation_name': 'authority_name',
        'organisation_url': 'authority_url',
        'organisation_address': 'authority_address',
        'instance_id': 'authority_instance_id',
        'object_id': 'authority_role_id',
        'status_id': 'authority_status_id',
    },
    'networks': {
        'administration_level_id': 'network_organisational_level_id',
    },
    'stations': {
        'eoi_code': 'station_eoi_code',
        'national_code': 'station_national_code',
        'area_classification_id': 'station_area_id',
    },
    'sampling_points': {
        'sampling_point_ref': 'sampling_point_reference_id',
        'spo_category_id': 'sampling_point_category_id',
    },
    'processes': {
        'activity_begin': 'process_activity_begin',
        'activity_end': 'process_activity_end',
    },
    'zones': {
        'code': 'zone_national_code',
        'area': 'zone_area',
    },
}


class Management:
    df = None
    df_schema = None
    table_name = None
    cursor = None
    exclude_list = []

    def __init__(self, cursor, table_name, exclude_list=[], naming='v1'):
        self.cursor = cursor
        self.table_name = table_name
        self.exclude_list = exclude_list
        self.naming = naming
        self.__get_db_schema()

    # -- header aliasing ----------------------------------------------------

    def _legacy_to_current(self):
        """{legacy header: current column} for this table, or {} under v2."""
        if self.naming != 'v1':
            return {}
        return V1_ALIASES.get(self.table_name, {})

    def _current_to_legacy(self):
        return {v: k for k, v in self._legacy_to_current().items()}

    def _rename_out(self, df):
        """Current columns -> the headers this API version publishes."""
        mapping = self._current_to_legacy()
        return df.rename(columns=mapping) if mapping and df is not None else df

    def _rename_in(self, df):
        """Incoming headers -> current column names."""
        mapping = self._legacy_to_current()
        return df.rename(columns=mapping) if mapping and df is not None else df

    def __get_db_schema(self):
        self.cursor.execute("SELECT case when udt_name = 'geometry' then 'st_astext('||column_name||') as ' || column_name else column_name end as prop_select, case when udt_name = 'geometry' then 'st_setsrid(ST_GeomFromText(%%('||column_name||')s),4326)' else '%%('||column_name||')s' end as prop_insert, column_name, udt_name as data_type, case when is_nullable = 'YES' then true else false end optional, case when column_default is null then false else true end has_default FROM information_schema.columns WHERE table_name = %(table)s order by ordinal_position", {"table": self.table_name})

        rows = self.cursor.fetchall()
        df_schema = pd.DataFrame.from_records(rows)
        self.exclude_column_names(df_schema, self.exclude_list)

    def parse_list(self, lst):
        self.df = self._rename_in(pd.DataFrame.from_records(lst))

        self.__validate()

    def exclude_column_names(self, df_schema, exclude_list):
        if len(exclude_list) > 0:
            for ex in exclude_list:
                df_schema = df_schema[df_schema.column_name != ex]
        self.df_schema = df_schema

    def parse_file(self, file):
        na_values = ['-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A N/A', '#N/A', 'N/A', 'n/a',  '', '#NA', 'NULL', 'null', 'NaN', '-NaN', 'nan', '-nan', '']
        if file.filename.endswith(".csv"):
            self.df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8")), skipinitialspace=True, keep_default_na=False, na_values=na_values)
        elif file.filename.endswith(".gpkg"):
            gdf = gp.read_file(file, driver="GPKG")
            gdf["geom"] = gdf.geometry.to_wkt()
            self.df = pd.DataFrame(gdf.drop(columns=['geometry']))  # Dont need geopandas geometry functionality anymore.

        else:
            raise BadRequest(f'File type is not supported: {file.filename}. '
                             f'Upload a .csv or .gpkg file.')

        # Accept the headers this API version publishes, then work internally
        # with the current column names.
        self.df = self._rename_in(self.df)

        self.__validate()

    # For the message when a value will not convert. The importer's own type names,
    # not the caller's, so an unmapped type still produces something readable.
    __TYPE_NAMES = {
        "numeric": "a number",
        "varchar": "text",
        "bool": "true or false",
        "geometry": "WKT geometry",
        "timestamp": "a timestamp",
        "timestamptz": "a timestamp",
        "date": "a date",
    }

    def __expected(self, row):
        if row.data_type.startswith("int"):
            return "a whole number"
        return self.__TYPE_NAMES.get(row.data_type, row.data_type)

    def __validate(self):
        self.df = self.df.astype(object)
        exclude_list = []
        for index, row in self.df_schema.iterrows():
            # If no column, but there is a default value in db
            if not row.column_name in self.df.columns and row.has_default:
                exclude_list.append(row.column_name)
                continue

            # Does it contain all required columns
            if not row.column_name in self.df.columns:
                raise BadRequest(
                    f'Header {row.column_name} was not found. The file must carry a column for '
                    f'every field of {self.table_name}: '
                    f'{", ".join(self.df_schema.column_name)}.')

            # Does it contain any null values if required
            if not row.optional and self.df[row.column_name].isnull().values.any():
                raise BadRequest(f'Column {row.column_name} cannot have empty values.')

            # A value that will not convert is the caller's data, not a server
            # fault, so report which column and what was expected rather than
            # letting a bare pandas or shapely error become a 500.
            try:
                self.__validate_column_type(row)
            except (BadRequest, NotImplementedError):
                # Already precise, or a raven gap rather than the caller's data.
                raise
            except Exception as e:
                raise BadRequest(
                    f'Column {row.column_name} expects {self.__expected(row)}, but a value '
                    f'could not be read: {e}') from e

        self.exclude_column_names(self.df_schema, exclude_list)

    def __validate_column_type(self, row):
        """Raise if any non-null value in the column will not convert."""
        if row.column_name.upper() == "BEGIN_POSITION" or row.column_name.upper() == "END_POSITION":
            pd.to_datetime(self.df[self.df[row.column_name].notna()][row.column_name], format="%Y-%m-%dT%H:%M:%S%z")

        elif row.data_type.startswith("int"):
            self.df[self.df[row.column_name].notna()][row.column_name].astype(int)

        elif row.data_type == "numeric":
            self.df[self.df[row.column_name].notna()][row.column_name].astype(float)

        elif row.data_type == "varchar":
            self.df[self.df[row.column_name].notna()][row.column_name].astype(str)

        elif row.data_type == "bool":
            bool_list = ['true', 'True', 'TRUE', True, 'false', 'False', 'FALSE', False]
            if (not self.df[row.column_name].isin(bool_list).any()) and (self.df[row.column_name].notna().any()):
                raise BadRequest(f'Column {row.column_name} must be a boolean value '
                                 f'(true or false).')

        elif row.data_type == "geometry":
            self.df[self.df[row.column_name].notna()][row.column_name].apply(wkt.loads)

        elif row.data_type in ("timestamp", "timestamptz", "date"):
            pd.to_datetime(self.df[self.df[row.column_name].notna()][row.column_name])

        else:
            # Not the caller's fault: the importer has no check for a type the
            # schema uses, so this stays a server error.
            raise NotImplementedError(
                f'{self.table_name}.{row.column_name} is {row.data_type}, which the management '
                f'importer has no validation for — add one to __validate_column_type.')

    def generic_select(self):
        sql = f"""
          select {','.join(self.df_schema.prop_select)} from {self.table_name} order by {self.df_schema.column_name.iloc[0]}
        """

        self.sql_select(sql)

    def sql_select(self, sql):
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        # Publish the headers this API version promises, not the raw columns.
        self.df = self._rename_out(DataFrame(rows))

    def generic_insert(self):
        sql = f"""
          insert into {self.table_name}
          ({','.join(self.df_schema.column_name)})
          values
          ({','.join(self.df_schema.prop_insert)})
        """

        self.sql_insert(sql)

    def sql_insert(self, sql):
        # convert NaN to None so that insert works as expected. Type must be object for None to be set
        df2 = self.df.where(pd.notnull(self.df), None)
        self.cursor.executemany(sql, df2.to_dict('records'))
