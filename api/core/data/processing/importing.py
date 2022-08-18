from pandas import DataFrame
import time
from api.core.printcol import printcol
from api.core.utils import U
from api.core.data.processing.scaling import Scaling
import pandas as pd


class Importing:

    @staticmethod
    def Import(cursor: any, df_values: DataFrame):

        # IMPORT FLOW
        # - Validates datatypes
        # - Add additional timeserie info to value
        # - Verify no duplicate times, is calculated etc
        # - Scale values if possible. Sets scaledvalue for non-scalables as importvalue
        # - Calculate new values if possible. Requires all timeseries to be present in importvalues or db. Uses value.scaledvalue to calculate
        # - Convert values if convertion factor is present.
        # - FillInMissing fills holes based on timestep. it uses timeserie totime or timevalue totime to determine the period to fill out
        # - DoFlagging sets the qa and qc flag based on a number of criterias, like scalingpoints and instrument flags. It also lookup values in database to change if we have multiple equal values in a row
        # - Upsert inserts or updates data to aqrw_rawdatavalues, aqte_timevalue and aqal_additionalloggervalues. It will not update values with qc >= 4. If QA has been manually set it will used the old qa instead of the new

        Importing.validate_dataframe(df_values)
        df_values = Importing.add_timeserie_info(cursor, df_values)
        Importing.verify_values(cursor, df_values)
        #Scaling.Scale(cursor, df_values)

        # Scale
        # Calculate
        # Convert
        # FillInMissing
        # DoFlagging
        # Insert
        pass

    @staticmethod
    def validate_dataframe(df_values: DataFrame):
        bench = time.perf_counter()
        # Validations raises an exception if it fails
        df_values["begin_position"] = pd.to_datetime(df_values["begin_position"], format="%Y-%m-%dT%H:%M:%S%Z")
        df_values["end_position"] = pd.to_datetime(df_values["end_position"], format="%Y-%m-%dT%H:%M:%S%Z")
        df_values.value.astype(float)
        df_values.verification_flag.astype(int)
        df_values.validation_flag.astype(int)
        printcol(f"- Validating datatypes took {time.perf_counter() - bench} seconds")

    @staticmethod
    def add_timeserie_info(cursor: any, df_values: pd.DataFrame):
        bench = time.perf_counter()
        ids = tuple(df_values.sampling_point_id.unique().tolist())
        sql = """
            select
                c.sampling_point_id,
                extract(epoch from c.from_time) as from_time,
                extract(epoch from c.to_time) as to_time,
                t.timestep, 
                case when cs.id is NULL then False else True end as is_calculated
            from
                eea_times t,
                observing_capabilities c left join calculated_series cs on cs.result = c.id
            where c.timestep = t.id
            and c.sampling_point_id in %(ids)s 
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

    @staticmethod
    def verify_values(cursor: any, df_values: DataFrame):
        bench = time.perf_counter()
        # Check for duplicate datetimes
        if len(df_values[df_values[['sampling_point_id', 'begin_position', 'end_position']].duplicated()]) > 0:
            raise Exception("A timeserie cannot contain duplicate datetimes")

        # Check if value has a samplingpoint
        if len(df_values[df_values["has_timeserie_info"] == False]) > 0:
            raise Exception("Not enough timeserie info to continue")

        # Check if any are calculated timeseries
        if len(df_values[df_values["ts_is_calculated"] == True]) > 0:
            raise Exception("Calculated values cannot be imported")

        # Check if all values have the same timezone
        if len(df_values["begin_position"].apply(lambda t: t.utcoffset().total_seconds()).unique()) > 1 or len(df_values["end_position"].apply(lambda t: t.utcoffset().total_seconds()).unique()) > 1:
            raise Exception("All values must have the same timezone ")

        printcol(f"- Verifying values took {time.perf_counter() - bench} seconds")
