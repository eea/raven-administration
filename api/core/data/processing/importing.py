import io
from pandas import DataFrame
import time
from core.data.processing.flagging import Flagging
from core.printcol import printcol
from core.utils import U
from core.data.processing.scaling import Scaling
from core.data.processing.calculation import Calculating
from core.data.processing.converting import Converting
from core.data.processing.filling import Filling
from core.data.processing.common import Common
import pandas as pd


class Importing:

    @staticmethod
    def Import(cursor: any, df_values: DataFrame):

        # IMPORT FLOW
        # - Validates datatypes
        # - Set import value
        # - Add additional timeserie info to value
        # - Verify no duplicate times, is calculated etc
        # - Scale values if possible.
        # - Calculate new values if possible.
        # - Convert values if convertion factor is present.
        # - FillInMissing fills holes based on timestep.
        # - DoFlagging
        # - Upsert inserts

        Common.validate_dataframe(df_values, cursor)
        Importing.set_import_value(df_values)
        df_values = Common.add_timeserie_info(cursor, df_values)
        Importing.verify_values(cursor, df_values)
        Scaling.Scale(cursor, df_values)
        df_values = Importing.process_scaled_values(cursor, df_values)
        df_values = Importing.upsert(cursor, df_values)
        pass

    @staticmethod
    def process_scaled_values(cursor, df_values: DataFrame, doFlagging: bool = True):
        df_values = Calculating.calculate(cursor, df_values)  # Rethink function for better performance
        Converting.convert(cursor, df_values)
        df_values = Filling.fillinmissing(cursor, df_values)  # Use pandas more active for better performance?

        if doFlagging:
            Flagging.flag(cursor, df_values)
        return df_values

    @staticmethod
    def set_import_value(df_values: DataFrame):
        bench = time.perf_counter()
        df_values["import_value"] = df_values["value"]
        df_values["scaled_value"] = None
        printcol(f"- Setting import value took {time.perf_counter() - bench} seconds")

    @staticmethod
    def verify_values(cursor: any, df_values: DataFrame):
        from core.data.processing.common import Common
        
        bench = time.perf_counter()
        # Check for duplicate datetimes
        if len(df_values[df_values[['sampling_point_id', 'from_time', 'to_time']].duplicated()]) > 0:
            raise Exception("A timeserie cannot contain duplicate datetimes")

        # Check if value has a samplingpoint
        if len(df_values[df_values["has_timeserie_info"] == False]) > 0:
            raise Exception("Not enough timeserie info to continue")

        # Check if any are calculated timeseries
        if len(df_values[df_values["ts_is_calculated"] == True]) > 0:
            raise Exception("Calculated values cannot be imported")

        # Check to see if timestep matches with the imported values. Ignore if timestep is -1
        df_errors = df_values[(((df_values.to_time - df_values.from_time) / pd.Timedelta(seconds=1)).astype('int64') - ((df_values.apply(lambda x: U.actual_timestep(x.from_time, x.ts_timestep), axis=1))).astype('int64')) > 0]
        df_errors = df_errors[df_errors.ts_timestep != -1]
        if len(df_errors) > 0:
            l = len(df_errors)
            f = df_errors.iloc[0]
            raise Exception(f"Imported values does not match timestep. First error is at {f.sampling_point_id} {f.from_time} {f.to_time} {f.ts_timestep}")

        # Check if all imported timestamps match the configured timezone
        expected_offset_minutes = Common.get_settings_timezone(cursor)
        actual_offsets = df_values["from_time"].apply(lambda t: t.utcoffset().total_seconds() / 60).unique()
        if len(actual_offsets) > 1:
            raise Exception(f"Imported data contains multiple timezones. All timestamps must have the same timezone.")
        if len(actual_offsets) > 0 and actual_offsets[0] != expected_offset_minutes:
            # Get timezone ID for error message
            cursor.execute("SELECT tz.id FROM settings s JOIN eea_timezones tz ON s.timezone_id = tz.id LIMIT 1")
            tz_row = cursor.fetchone()
            expected_tz = tz_row["id"] if tz_row else "UTC"
            actual_offset_hours = int(actual_offsets[0] / 60)
            actual_tz = f"UTC{actual_offset_hours:+03d}".replace("+00", "")  # Format as UTC+01 or UTC-05
            if actual_tz == "UTC":
                actual_tz = "UTC"
            raise Exception(f"Imported data timezone ({actual_tz}) does not match configured timezone ({expected_tz}). Please check your data or update settings.")

        # Check if any are verified values
        # if len(df_values[df_values["observationverification_id"] == 1]) > 0:
        #     raise Exception("Imported values cannot be verified")

        printcol(f"- Verifying values took {time.perf_counter() - bench} seconds")

    @staticmethod
    def upsert(cursor: any, df_values: DataFrame):
        # Use COPY FROM to copy data into a temp table
        # Then update those data in the observations data.
        # Data that was not updated are inserted.
        # Do it this way for performance reason. Db.executemany is too slow with a lot of data

        bench = time.perf_counter()
        sql = """
            WITH updates AS (
                UPDATE observations as t 
                SET
                    value = s.value,
                    observationverification_id = s.observationverification_id,
                    observationvalidity_id = s.observationvalidity_id,
                    touched = now(),
                    import_value = s.import_value,
                    scaled_value = s.scaled_value
                FROM source s
                WHERE t.sampling_point_id = s.sampling_point_id
                AND t.from_time = s.from_time
                AND t.to_time = s.to_time
                RETURNING t.sampling_point_id, t.from_time, t.to_time
            )
            INSERT INTO observations (sampling_point_id, from_time, to_time, value, observationverification_id, observationvalidity_id, import_value,scaled_value, touched)
            SELECT v.*, now() as touched
            FROM source v
            WHERE NOT EXISTS (
                SELECT 1
                FROM updates u
                WHERE u.sampling_point_id = v.sampling_point_id
                AND u.from_time = v.from_time
                and u.to_time = v.to_time 
            )
        """

        # tic = time.perf_counter()
        d = Importing.__data2io__(df_values)
        cols = ('sampling_point_id', 'from_time', 'to_time', 'value', 'observationverification_id', 'observationvalidity_id', 'import_value', 'scaled_value')
        cursor.execute('CREATE TEMP TABLE source(sampling_point_id varchar(100), from_time varchar(25), to_time varchar(25),value numeric(255,5), observationverification_id integer,observationvalidity_id integer, import_value numeric(255,5), scaled_value numeric(255,5)) ON COMMIT DROP;')
        cursor.copy_from(d, 'source', columns=cols, null='None')
        cursor.execute(sql)
        cursor.execute('DROP TABLE source')

        printcol(f"- Importing to db values took {time.perf_counter() - bench} seconds")

    @staticmethod
    def __data2io__(df_values: DataFrame):
        data = df_values.to_dict("records")
        si = io.StringIO()
        for row in data:
            si.write(f"{row['sampling_point_id']}\t{row['from_time'].isoformat()}\t{row['to_time'].isoformat()}\t{row['value']}\t{row['observationverification_id']}\t{row['observationvalidity_id']}\t{row['import_value']}\t{row['scaled_value']}\n")
        si.seek(0)
        return si
