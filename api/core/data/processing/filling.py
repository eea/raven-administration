from datetime import datetime
from pandas import DataFrame
import pandas as pd
import time
from core.printcol import printcol
from core.utils import U


class Filling:
    @staticmethod
    def fillinmissing(cursor: any, df_values: DataFrame):
        bench = time.perf_counter()
        missing_values = []
        timeseries = df_values.groupby("sampling_point_id")
        for key, values in timeseries:
            ts_from_epoch = values.ts_from_epoch.iloc[0]
            ts_to_epoch = values.ts_to_epoch.iloc[0]
            ts_timestep = values.ts_timestep.iloc[0]

            if ts_timestep == -1:
                continue

            scaled_value = -9900 if values.scaled_value.iloc[0] != None else None
            tz = values.end_position.iloc[0].strftime('%z')
            tz = "{0}:{1}".format(tz[:-2], tz[-2:])
            dates = values.end_position.apply(lambda x: x.timestamp()).unique()
            from_time = dates.min() if ts_to_epoch == None else dates.min() if ts_to_epoch > dates.min() else ts_to_epoch
            to_time = dates.max() if ts_to_epoch == None else dates.max() if ts_to_epoch < dates.max() else ts_from_epoch if ts_from_epoch > dates.max() else dates.max()

            existing_dates = Filling.__existing_dates__(cursor, key, from_time, to_time)
            date_range = [from_time+(d*ts_timestep) for d in range(0, int((to_time - from_time)/ts_timestep)+1)]
            dates_not_in_db = list(set(date_range) - set(existing_dates))
            missing_dates = list(set(dates_not_in_db) - set(dates))

            for m in missing_dates:
                v = {
                    "sampling_point_id": key,
                    "begin_position": pd.to_datetime(datetime.fromtimestamp(m-ts_timestep).strftime('%Y-%m-%dT%H:%M:%S')+tz, format="%Y-%m-%dT%H:%M:%S%Z"),
                    "end_position": pd.to_datetime(datetime.fromtimestamp(m).strftime('%Y-%m-%dT%H:%M:%S')+tz, format="%Y-%m-%dT%H:%M:%S%Z"),
                    "value": -9900,
                    "verification_flag": 3,
                    "validation_flag": -1,
                    "import_value": -9900,
                    "scaled_value": scaled_value
                }
                missing_values.append(v)

        printcol(f"- FillInMissing took {time.perf_counter() - bench} seconds")
        df_values = pd.concat([df_values, pd.DataFrame(missing_values)], axis=0)
        return df_values.reset_index(drop=True)

    @staticmethod
    def __timeseries__(cursor: any, sampling_point_ids: tuple):
        sql = """
            select p.id as sampling_point_id, extract(epoch from p.from_time) as from_time, extract(epoch from p.to_time) as to_time, t.timestep
            from sampling_points p, eea_times t
            where p.timestep = t.id
            and p.id in %(ids)s 
        """
        cursor.execute(sql, {"ids": sampling_point_ids})
        return cursor.fetchall()

    def __existing_dates__(cursor: any, sampling_point_id, epoch_from, epoch_to):
        sql = """
            select extract(epoch from from_time) as begin_position
            from observations o
            where o.sampling_point_id = %(sp)s
            and  extract(epoch from o.from_time) >= %(epoch_from)s
            and  extract(epoch from o.from_time) <= %(epoch_to)s  
        """
        cursor.execute(sql, {"sp": sampling_point_id, "epoch_from": epoch_from, "epoch_to": epoch_to})
        return list(map(lambda x: x["begin_position"], cursor.fetchall()))
