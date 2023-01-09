import pandas as pd
from pandas import DataFrame
import geopandas as gp
import io
from shapely import wkt


class Management:
    df = None
    df_schema = None
    table_name = None
    cursor = None
    exclude_list = []

    def __init__(self, cursor, table_name, exclude_list=[]):
        self.cursor = cursor
        self.table_name = table_name
        self.exclude_list = exclude_list
        self.__get_db_schema()

    def __get_db_schema(self):
        self.cursor.execute("SELECT case when udt_name = 'geometry' then 'st_astext('||column_name||') as ' || column_name else column_name end as prop_select, case when udt_name = 'geometry' then 'st_setsrid(ST_GeomFromText(%%('||column_name||')s),4326)' else '%%('||column_name||')s' end as prop_insert, column_name, udt_name as data_type, case when is_nullable = 'YES' then true else false end optional, case when column_default is null then false else true end has_default FROM information_schema.columns WHERE table_name = %(table)s order by ordinal_position", {"table": self.table_name})

        rows = self.cursor.fetchall()
        df_schema = pd.DataFrame.from_records(rows)
        self.exclude_column_names(df_schema, self.exclude_list)

    def parse_list(self, lst):
        self.df = pd.DataFrame.from_records(lst)

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
            raise Exception("File type is not supported")

        self.__validate()

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
                raise Exception("Header " + row.column_name + " was not found")

            # Does it contain any null values if required
            if not row.optional and self.df[row.column_name].isnull().values.any():
                raise Exception("Column " + row.column_name + " cannot have empty values")

            # Validations raises an exception if it fails
            if row.column_name.upper() == "BEGIN_POSITION" or row.column_name.upper() == "END_POSITION":
                pd.to_datetime(self.df[self.df[row.column_name].notna()][row.column_name], format="%Y-%m-%dT%H:%M:%S%Z")

            elif row.data_type.startswith("int"):
                self.df[self.df[row.column_name].notna()][row.column_name].astype(int)

            elif row.data_type == "numeric":
                self.df[self.df[row.column_name].notna()][row.column_name].astype(float)

            elif row.data_type == "varchar":
                self.df[self.df[row.column_name].notna()][row.column_name].astype(str)

            elif row.data_type == "bool":
                bool_list = ['true', 'True', 'TRUE', True, 'false', 'False', 'FALSE', False]
                if (not self.df[row.column_name].isin(bool_list).any()) and (self.df[row.column_name].notna().any()):
                    raise Exception("Column " + row.column_name + " must be boolean value")

            elif row.data_type == "geometry":
                self.df[self.df[row.column_name].notna()][row.column_name].apply(wkt.loads)

            else:
                raise Exception("Not implemented check for type: " + row.data_type)

        self.exclude_column_names(self.df_schema, exclude_list)

    def generic_select(self):
        sql = f"""
          select {','.join(self.df_schema.prop_select)} from {self.table_name} order by {self.df_schema.column_name.iloc[0]}
        """

        self.sql_select(sql)

    def sql_select(self, sql):
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        self.df = DataFrame(rows)

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
