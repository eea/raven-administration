from pandas import DataFrame
import pandas as pd
import time
from core.printcol import printcol


class Filling:
    @staticmethod
    def fillinmissing(cursor: any, df_values: DataFrame):
        """Fill in missing timestamps based on timestep for each sampling point."""
        bench = time.perf_counter()
        missing_values = []
        timeseries = df_values.groupby("sampling_point_id")
        
        for key, values in timeseries:
            ts_timestep = values.ts_timestep.iloc[0]
            
            # Skip if no timestep defined or irregular timestep
            if ts_timestep == -1 or pd.isna(ts_timestep):
                continue
            
            ts_timestep = int(ts_timestep)
            scaled_value = -9900 if values.scaled_value.iloc[0] is not None else None
            
            # Get imported to_times as set for fast lookup
            imported_to_times = set(values.to_time)
            min_time = values.to_time.min()
            max_time = values.to_time.max()
            
            # Extend range if sampling_point has earlier data in DB
            ts_to_epoch = values.ts_to_epoch.iloc[0]
            if pd.notna(ts_to_epoch):
                sp_to_time = pd.Timestamp(ts_to_epoch, unit='s')
                if sp_to_time < min_time:
                    min_time = sp_to_time + pd.Timedelta(seconds=ts_timestep)
            
            # Generate expected timestamps using pandas date_range
            expected_to_times = set(pd.date_range(start=min_time, end=max_time, freq=f'{ts_timestep}s'))
            
            # Get existing timestamps from DB
            existing_to_times = Filling.__existing_to_times__(cursor, key, min_time, max_time)
            
            # Find missing = expected - already_in_db - imported
            missing_to_times = expected_to_times - existing_to_times - imported_to_times
            
            # Create fill-in values
            for to_time in missing_to_times:
                from_time = to_time - pd.Timedelta(seconds=ts_timestep)
                missing_values.append({
                    "sampling_point_id": key,
                    "from_time": from_time,
                    "to_time": to_time,
                    "value": -9900,
                    "observationverification_id": 3,
                    "observationvalidity_id": -1,
                    "import_value": -9900,
                    "scaled_value": scaled_value
                })
        
        if missing_values:
            df_values = pd.concat([df_values, pd.DataFrame(missing_values)], axis=0)
        
        printcol(f"- FillInMissing took {time.perf_counter() - bench} seconds")
        return df_values.reset_index(drop=True)

    @staticmethod
    def __existing_to_times__(cursor, sampling_point_id, min_time, max_time):
        """Get existing to_time values from DB as pandas Timestamps."""
        sql = """
            SELECT to_time
            FROM observations
            WHERE sampling_point_id = %(sp)s
            AND to_time >= %(min_time)s
            AND to_time <= %(max_time)s  
        """
        cursor.execute(sql, {"sp": sampling_point_id, "min_time": min_time, "max_time": max_time})
        return set(pd.Timestamp(row["to_time"]) for row in cursor.fetchall())
