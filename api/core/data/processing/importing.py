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

        Common.validate_dataframe(df_values)
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

        # Check to see if timestep matches with the imported values. Ignore if timestep is 1
        if not (((df_values.end_position - df_values.begin_position) / pd.Timedelta(seconds=1) == (df_values.apply(lambda x: U.actual_timestep(x.begin_position, x.ts_timestep), axis=1)))).all() and not (df_values.ts_timestep == -1).all():
            raise Exception("The difference between end_position and begin_position must be the same as the samplingpoint timestep")

        # Check if any are verified values
        # if len(df_values[df_values["verification_flag"] == 1]) > 0:
        #     raise Exception("Imported values cannot be verified")

        # Check if all values have the same timezone
        if len(df_values["begin_position"].apply(lambda t: t.utcoffset().total_seconds()).unique()) > 1 or len(df_values["end_position"].apply(lambda t: t.utcoffset().total_seconds()).unique()) > 1:
            raise Exception("All values must have the same timezone ")

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
                    verification_flag = s.verification_flag,
                    validation_flag = s.validation_flag,
                    touched = now(),
                    import_value = s.import_value,
                    scaled_value = s.scaled_value
                FROM source s
                WHERE t.sampling_point_id = s.sampling_point_id
                AND t.begin_position = s.begin_position
                AND t.end_position = s.end_position
                RETURNING t.sampling_point_id, t.begin_position, t.end_position
            )
            INSERT INTO observations (sampling_point_id, begin_position, end_position, value, verification_flag, validation_flag, import_value,scaled_value, touched)
            SELECT v.*, now() as touched
            FROM source v
            WHERE NOT EXISTS (
                SELECT 1
                FROM updates u
                WHERE u.sampling_point_id = v.sampling_point_id
                AND u.begin_position = v.begin_position
                and u.end_position = v.end_position 
            )
        """

        #tic = time.perf_counter()
        d = Importing.__data2io__(df_values)
        cols = ('sampling_point_id', 'begin_position', 'end_position', 'value', 'verification_flag', 'validation_flag', 'import_value', 'scaled_value')
        cursor.execute('CREATE TEMP TABLE source(sampling_point_id varchar(100), begin_position varchar(25), end_position varchar(25),value numeric(255,5), verification_flag integer,validation_flag integer, import_value numeric(255,5), scaled_value numeric(255,5)) ON COMMIT DROP;')
        cursor.copy_from(d, 'source', columns=cols, null='None')
        cursor.execute(sql)
        cursor.execute('DROP TABLE source')

        printcol(f"- Importing to db values took {time.perf_counter() - bench} seconds")

    @staticmethod
    def __data2io__(df_values: DataFrame):
        data = df_values.to_dict("records")
        si = io.StringIO()
        for row in data:
            si.write(f"{row['sampling_point_id']}\t{row['begin_position']}\t{row['end_position']}\t{row['value']}\t{row['verification_flag']}\t{row['validation_flag']}\t{row['import_value']}\t{row['scaled_value']}\n")
        si.seek(0)
        return si
