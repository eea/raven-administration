import pandas as pd
from pandas import DataFrame
import io


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

    def parse_file(self, file):
        self.df = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8")), skipinitialspace=True)
        self.__validate()

    def generic_select(self):
        sql = f"""
          select {','.join(self.df_schema.column_name)} from {self.table_name} order by {self.df_schema.column_name.iloc[0]}
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
          ({'%('}{')s,%('.join(self.df_schema.column_name)}{')s'})
        """

        self.sql_insert(sql)

    def sql_insert(self, sql):
        # convert NaN to None so that insert works as expected. Type must be object for None to be set
        self.df = self.df.astype(object)
        df2 = self.df.where(pd.notnull(self.df), None)

        self.cursor.executemany(sql, df2.to_dict('records'))

    def __get_db_schema(self):
        self.cursor.execute("SELECT column_name, udt_name as data_type, case when is_nullable = 'YES' then true else false end optional FROM information_schema.columns WHERE table_name = %(table)s order by ordinal_position", {"table": self.table_name})
        rows = self.cursor.fetchall()
        df_schema = pd.DataFrame.from_records(rows)
        # only works with point
        if "geometry" in df_schema.data_type.values:
            cols = [
                {"column_name": "latitude", "data_type": "numeric", "optional": False},
                {"column_name": "longitude", "data_type": "numeric", "optional": False},
                {"column_name": "altitude", "data_type": "numeric", "optional": False},
                {"column_name": "epsg", "data_type": "integer", "optional": False}
            ]
            df_schema = df_schema[df_schema.data_type != "geometry"]
            df_schema = pd.concat([pd.DataFrame.from_records(cols), df_schema], ignore_index=True)

        if len(self.exclude_list) > 0:
            for ex in self.exclude_list:
                df_schema = df_schema[df_schema.column_name != ex]

        self.df_schema = df_schema

    def __validate(self):
        self.df = self.df.astype(object)
        for index, row in self.df_schema.iterrows():
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

            else:
                raise Exception("Not implemented check for type: " + row.data_type)
