from pandas import DataFrame
import pandas as pd
import time
from core.printcol import printcol


class Common:
    @staticmethod
    def get_settings_timezone(cursor):
        """Get the configured timezone from settings"""
        cursor.execute("SELECT tz.id FROM settings s JOIN eea_timezones tz ON s.timezone_id = tz.id LIMIT 1")
        row = cursor.fetchone()
        if row:
            # Convert "UTC+01" format to offset minutes for pytz.FixedOffset
            tz_str = row["id"]
            if tz_str == "UTC":
                return 0
            # Parse UTC+01, UTC-05, etc.
            sign = 1 if "+" in tz_str else -1
            offset_hours = int(tz_str.split("+")[-1].split("-")[-1])
            return sign * offset_hours * 60
        return 0  # Default to UTC if no settings

    @staticmethod
    def validate_dataframe(df_values: DataFrame):
        bench = time.perf_counter()
        if df_values.empty:
            printcol(f"- Validating datatypes took {time.perf_counter() - bench} seconds (empty dataframe)")
            return
        
        # Map old column names to new column names for backwards compatibility
        column_mapping = {
            "begin_position": "from_time",
            "end_position": "to_time",
            "verification_flag": "observationverification_id",
            "validation_flag": "observationvalidity_id"
        }
        df_values.rename(columns={k: v for k, v in column_mapping.items() if k in df_values.columns}, inplace=True)
        
        # Convert datatypes
        df_values["from_time"] = pd.to_datetime(df_values["from_time"])
        df_values["to_time"] = pd.to_datetime(df_values["to_time"])
        df_values["sampling_point_id"] = df_values["sampling_point_id"].astype(str)
        df_values["value"] = df_values["value"].astype(float)
        df_values["observationverification_id"] = df_values["observationverification_id"].astype(int)
        df_values["observationvalidity_id"] = df_values["observationvalidity_id"].astype(int)
        
        printcol(f"- Validating datatypes took {time.perf_counter() - bench} seconds")

    @staticmethod
    def add_timeserie_info(cursor: any, df_values: pd.DataFrame):
        bench = time.perf_counter()
        # Return empty dataframe if input is empty
        if df_values.empty:
            printcol(f"- Adding timeserie info took {time.perf_counter() - bench} seconds (empty dataframe)")
            return df_values
        ids = tuple(df_values.sampling_point_id.unique().tolist())
        sql = """
            select
                p.id as sampling_point_id,
                extract(epoch from p.from_time)::float as from_time,
                extract(epoch from p.to_time)::float as to_time,
                case when t.timestep = 1 and t.notation != 's' then -1 else t.timestep end as timestep,
                case when cs.id is NULL then False else True end as is_calculated
            from
                eea_times t,
                sampling_points p left join calculated_series cs on cs.result = p.id
            where p.time_resolution_id = t.id
            and p.id in %(ids)s
        """
        cursor.execute(sql, {"ids": ids})
        timeseries = cursor.fetchall()

        grouped = df_values.groupby("sampling_point_id")

        new_table = []
        for key, group in grouped:
            timeserie = next(filter(lambda t: t["sampling_point_id"] == key, timeseries), None)
            if timeserie is not None:
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
