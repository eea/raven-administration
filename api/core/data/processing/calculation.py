from pandas import DataFrame
import pandas as pd
import time
from core.data.processing.common import Common
from core.printcol import printcol


class Calculating:

    @staticmethod
    def calculate(cursor: any, df_values: DataFrame):
        bench = time.perf_counter()
        calculated_values = []
        calculated_timeseries = Calculating.__calculated_timeseries__(cursor)

        primaries = list(map(lambda x: x["primary"], calculated_timeseries))
        secondaries = list(map(lambda x: x["secondary"], calculated_timeseries))
        calculated_ids = primaries + secondaries
        filtered_values = df_values[df_values.sampling_point_id.isin(calculated_ids)]
        if filtered_values.empty:
            printcol(f"- Calculating took {time.perf_counter() - bench} seconds")
            return df_values

        grouped_values = filtered_values.groupby("to_time")

        to_time_min = filtered_values.to_time.min()
        to_time_max = filtered_values.to_time.max()

        scaled_db_values = Calculating.__get_all_scaled_value_from_db__(cursor, tuple(calculated_ids), to_time_min, to_time_max)

        # Build lookup dict for O(1) access instead of O(n) filtering
        db_lookup = {(r["sampling_point_id"], pd.Timestamp(r["to_time"])): r for r in scaled_db_values}

        for key, group in grouped_values:
            for cs in calculated_timeseries:
                pri = group[(group["sampling_point_id"] == cs["primary"])]
                sec = group[(group["sampling_point_id"] == cs["secondary"])]

                if pri.empty and sec.empty:
                    continue

                elif not pri.empty and not sec.empty:
                    pri_val = pri.iloc[0]["scaled_value"]
                    sec_val = sec.iloc[0]["scaled_value"]
                    if pri_val is not None and sec_val is not None:
                        calculated_value = Calculating.__create_observation__(cs["result"], pri_val, sec_val, cs["operator"], pri.iloc[0]["observationvalidity_id"], sec.iloc[0]["observationvalidity_id"], pri.iloc[0]["from_time"], pri.iloc[0]["to_time"])
                        calculated_values.append(calculated_value)

                elif not pri.empty:
                    pri_val = pri.iloc[0]["scaled_value"]
                    if pri_val is not None:
                        obs = db_lookup.get((cs["secondary"], key))
                        if obs is not None and obs["value"] is not None:
                            calculated_value = Calculating.__create_observation__(cs["result"], pri_val, obs["value"], cs["operator"], pri.iloc[0]["observationvalidity_id"], obs["observationvalidity_id"], pri.iloc[0]["from_time"], pri.iloc[0]["to_time"])
                            calculated_values.append(calculated_value)

                elif not sec.empty:
                    sec_val = sec.iloc[0]["scaled_value"]
                    if sec_val is not None:
                        obs = db_lookup.get((cs["primary"], key))
                        if obs is not None and obs["value"] is not None:
                            calculated_value = Calculating.__create_observation__(cs["result"], obs["value"], sec_val, cs["operator"], obs["observationvalidity_id"], sec.iloc[0]["observationvalidity_id"], sec.iloc[0]["from_time"], sec.iloc[0]["to_time"])
                            calculated_values.append(calculated_value)

        printcol(f"- Calculating took {time.perf_counter() - bench} seconds")

        df_calculated_values = Common.add_timeserie_info(cursor, pd.DataFrame(calculated_values))
        df_values = pd.concat([df_values, df_calculated_values], axis=0)
        return df_values.reset_index(drop=True)

    @staticmethod
    def __calculated_timeseries__(cursor: any):
        sql = """
            select cs.*
            from calculated_series cs 
        """
        cursor.execute(sql)
        return cursor.fetchall()

    @staticmethod
    def __create_observation__(sampling_point_id, value_pri, value_sec, operator, validate_pri, validate_sec, from_time, to_time):
        val = eval(str(value_pri) + operator + str(value_sec))
        is_valid = int(validate_pri) > 0 and int(validate_sec) > 0
        return {"sampling_point_id": sampling_point_id, "value": val, "import_value": val, "scaled_value": val, "observationverification_id": 3, "observationvalidity_id": 1 if is_valid else -1, "from_time": from_time, "to_time": to_time}

    @staticmethod
    def __get_all_scaled_value_from_db__(cursor: any, sampling_point_ids, min, max):
        sql = """
            select o.sampling_point_id, o.to_time, o.scaled_value as value, o.observationvalidity_id
            from observations o
            where o.sampling_point_id in %(s)s
            and o.from_time >=  %(min)s
            and o.from_time <  %(max)s
        """
        cursor.execute(sql, {"s": sampling_point_ids, "min":  min, "max": max})
        return cursor.fetchall()
