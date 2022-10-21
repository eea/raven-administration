from pandas import DataFrame
import pandas as pd
import time
from api.core.printcol import printcol


class Common:
    @staticmethod
    def validate_dataframe(df_values: DataFrame):
        bench = time.perf_counter()
        # Validations raises an exception if it fails
        df_values["begin_position"] = pd.to_datetime(df_values["begin_position"], format="%Y-%m-%dT%H:%M:%S%Z")
        df_values["end_position"] = pd.to_datetime(df_values["end_position"], format="%Y-%m-%dT%H:%M:%S%Z")
        df_values.sampling_point_id.astype(str)
        df_values.value = df_values.value.astype(float)
        df_values.verification_flag.astype(int)
        df_values.validation_flag.astype(int)
        printcol(f"- Validating datatypes took {time.perf_counter() - bench} seconds")

    @staticmethod
    def add_timeserie_info(cursor: any, df_values: pd.DataFrame):
        bench = time.perf_counter()
        ids = tuple(df_values.sampling_point_id.unique().tolist())
        sql = """
            select
                p.id as sampling_point_id,
                extract(epoch from p.from_time) as from_time,
                extract(epoch from p.to_time) as to_time,
                t.timestep,
                case when cs.id is NULL then False else True end as is_calculated
            from
                eea_times t,
                sampling_points p left join calculated_series cs on cs.result = p.id
            where p.timestep = t.id
            and p.id in %(ids)s
        """
        cursor.execute(sql, {"ids": ids})
        timeseries = cursor.fetchall()

        grouped = df_values.groupby("sampling_point_id")

        new_table = []
        for key, group in grouped:
            timeserie = next(filter(lambda t: t["sampling_point_id"] == key, timeseries), None)
            if timeserie != None:
                group["ts_from_epoch"] = timeserie["from_time"]
                group["ts_to_epoch"] = timeserie["to_time"]
                group["ts_timestep"] = timeserie["timestep"]
                group["ts_is_calculated"] = timeserie["is_calculated"]
                group["has_timeserie_info"] = True
            else:
                group["ts_from_epoch"] = None
                group["ts_to_epoch"] = None
                group["ts_timestep"] = None
                group["ts_is_calculated"] = None
                group["has_timeserie_info"] = False
            new_table.append(group.copy())

        df = pd.concat(new_table).reset_index(drop=True)

        printcol(f"- Adding timeserie info took {time.perf_counter() - bench} seconds")
        return df
