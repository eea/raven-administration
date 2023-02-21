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

        grouped_values = filtered_values.groupby("end_position")

        end_positions_min = filtered_values.end_position.min().strftime('%Y-%m-%dT%H:%M:%S%z')
        end_positions_max = filtered_values.end_position.max().strftime('%Y-%m-%dT%H:%M:%S%z')
        ids = filtered_values.sampling_point_id.unique()

        scaled_db_values = Calculating.__get_all_scaled_value_from_db__(cursor, tuple(ids), end_positions_min, end_positions_max)

        for key, group in grouped_values:
            for cs in calculated_timeseries:
                pri = group[(group["sampling_point_id"] == cs["primary"])]
                sec = group[(group["sampling_point_id"] == cs["secondary"])]
                end_position_str = key.strftime('%Y-%m-%dT%H:%M:%S%z')
                end_position_str = "{0}:{1}".format(end_position_str[:-2], end_position_str[-2:])

                if pri.empty and sec.empty:
                    continue

                elif not pri.empty and not sec.empty:
                    calculated_value = Calculating.__create_observation__(cs["result"], pri.iloc[0]["value"], sec.iloc[0]["value"], cs["operator"], pri.iloc[0]["validation_flag"], sec.iloc[0]["validation_flag"], pri.iloc[0]["begin_position"], pri.iloc[0]["end_position"])
                    calculated_values.append(calculated_value)

                elif not pri.empty:
                    obs = next(filter(lambda x: x["sampling_point_id"] == cs["secondary"] and x["end_position"] == end_position_str, scaled_db_values), None)  # Calculating.__get_scaled_value_from_db__(cursor, cs["secondary"], end_position_str)
                    if obs is not None:
                        calculated_value = Calculating.__create_observation__(cs["result"], pri.iloc[0]["value"], obs["value"], cs["operator"], pri.iloc[0]["validation_flag"], obs["validation_flag"], pri.iloc[0]["begin_position"], pri.iloc[0]["end_position"])
                        calculated_values.append(calculated_value)

                elif not sec.empty:
                    obs = next(filter(lambda x: x["sampling_point_id"] == cs["primary"] and x["end_position"] == end_position_str, scaled_db_values), None)  # Calculating.__get_scaled_value_from_db__(cursor, cs["primary"], end_position_str)
                    if obs is not None:
                        calculated_value = Calculating.__create_observation__(cs["result"], obs["value"], sec.iloc[0]["value"], cs["operator"], obs["validation_flag"], sec.iloc[0]["validation_flag"], sec.iloc[0]["begin_position"], sec.iloc[0]["end_position"])
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
    def __create_observation__(sampling_point_id, value_pri, value_sec, operator, validate_pri, validate_sec, begin_position, end_position):
        val = eval(str(value_pri) + operator + str(value_sec))
        is_valid = int(validate_pri) > 0 and int(validate_sec) > 0
        return {"sampling_point_id": sampling_point_id, "value": val, "import_value": val, "scaled_value": val, "verification_flag": 3, "validation_flag": 1 if is_valid else -1, "begin_position": begin_position, "end_position": end_position}

    @staticmethod
    def __get_all_scaled_value_from_db__(cursor: any, sampling_point_ids, min, max):
        sql = """
            select o.sampling_point_id, o.end_position, o.scaled_value as value
            from observations o
            where o.sampling_point_id in %(s)s
            and o.from_time >=  %(min)s
            and o.from_time <  %(max)s
        """
        cursor.execute(sql, {"s": sampling_point_ids, "min":  min, "max": max})
        return cursor.fetchall()
