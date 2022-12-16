from pandas import DataFrame
import time
from core.printcol import printcol


class Converting:
    @staticmethod
    def convert(cursor: any, df_values: DataFrame):
        bench = time.perf_counter()
        converted_timeseries = Converting.__converted_timeseries__(cursor)

        for c in converted_timeseries:
            df_values = df_values[(df_values.sampling_point_id == c["sampling_point_id"])].assign(value=df_values["value"] * float(c["factor"]))

        # filtered_values = df_values[df_values.sampling_point_id.isin(map(lambda x: x["sampling_point_id"], converted_timeseries))]
        # for row in filtered_values.itertuples():
        #     converted_timeserie = next(filter(lambda x: x["sampling_point_id"] == row.sampling_point_id, converted_timeseries), None)
        #     if converted_timeserie is not None:
        #         df_values.at[row.Index,  "value"] = row.value * float(converted_timeserie["factor"])

        printcol(f"- Converting took {time.perf_counter() - bench} seconds")

    @staticmethod
    def __converted_timeseries__(cursor: any):
        sql = """
            select cs.*
            from converted_series cs
        """
        cursor.execute(sql)
        return cursor.fetchall()
