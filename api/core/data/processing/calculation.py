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

        primaries = map(lambda x: x["primary"], calculated_timeseries)
        secondaries = map(lambda x: x["secondary"], calculated_timeseries)
        calculated_ids = list(primaries) + list(secondaries)
        filtered_values = df_values[df_values.sampling_point_id.isin(calculated_ids)]
        if filtered_values.empty:
            printcol(f"- Calculating took {time.perf_counter() - bench} seconds")
            return df_values

        grouped_values = filtered_values.groupby("to_time")

        to_time_min = filtered_values.to_time.min().strftime('%Y-%m-%dT%H:%M:%S%z')
        to_time_max = filtered_values.to_time.max().strftime('%Y-%m-%dT%H:%M:%S%z')
        ids = filtered_values.sampling_point_id.unique()

        scaled_db_values = Calculating.__get_all_scaled_value_from_db__(cursor, tuple(ids), to_time_min, to_time_max)

        for key, group in grouped_values:
            for cs in calculated_timeseries:
                pri = group[(group["sampling_point_id"] == cs["primary"])]
                sec = group[(group["sampling_point_id"] == cs["secondary"])]
                to_time_str = key.strftime('%Y-%m-%dT%H:%M:%S%z')
                to_time_str = "{0}:{1}".format(to_time_str[:-2], to_time_str[-2:])

                if pri.empty and sec.empty:
                    continue

                elif not pri.empty and not sec.empty:
                    calculated_value = Calculating.__create_observation__(cs["result"], pri.iloc[0]["value"], sec.iloc[0]["value"], cs["operator"], pri.iloc[0]["observationvalidity_id"], sec.iloc[0]["observationvalidity_id"], pri.iloc[0]["from_time"], pri.iloc[0]["to_time"])
                    calculated_values.append(calculated_value)

                elif not pri.empty:
                    obs = next(filter(lambda x: x["sampling_point_id"] == cs["secondary"] and x["to_time"] == to_time_str, scaled_db_values), None)
                    if obs is not None:
                        calculated_value = Calculating.__create_observation__(cs["result"], pri.iloc[0]["value"], obs["value"], cs["operator"], pri.iloc[0]["observationvalidity_id"], obs["observationvalidity_id"], pri.iloc[0]["from_time"], pri.iloc[0]["to_time"])
                        calculated_values.append(calculated_value)

                elif not sec.empty:
                    obs = next(filter(lambda x: x["sampling_point_id"] == cs["primary"] and x["to_time"] == to_time_str, scaled_db_values), None)
                    if obs is not None:
                        calculated_value = Calculating.__create_observation__(cs["result"], obs["value"], sec.iloc[0]["value"], cs["operator"], obs["observationvalidity_id"], sec.iloc[0]["observationvalidity_id"], sec.iloc[0]["from_time"], sec.iloc[0]["to_time"])
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
