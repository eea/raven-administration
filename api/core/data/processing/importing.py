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
        df_values = Filling.fillinmissing(cursor, df_values)

        if doFlagging:
            Flagging.flag(cursor, df_values)
        return df_values

    @staticmethod
    def set_import_value(df_values: DataFrame):
        bench = time.perf_counter()
        # Replace empty strings, None, and NaN with the sentinel value -9900
        df_values["value"] = pd.to_numeric(df_values["value"], errors="coerce").fillna(-9900)
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

        # Block import if any existing observations in the date range are verified (observationverification_id = 1).
        # This includes calculated series results (e.g. NO from NOX-NO2=NO) that would be overwritten
        # by Calculating.calculate() later in the pipeline.
        sp_ids = df_values["sampling_point_id"].unique().tolist()
        min_time = df_values["from_time"].min()
        max_time = df_values["to_time"].max()
        cursor.execute(
            """
            SELECT "result" FROM calculated_series
            WHERE "primary" = ANY(%(sp_ids)s) OR secondary = ANY(%(sp_ids)s)
            """,
            {"sp_ids": sp_ids},
        )
        calculated_result_ids = [row["result"] for row in cursor.fetchall()]
        all_sp_ids = sp_ids + calculated_result_ids

        cursor.execute(
            """
            SELECT sampling_point_id, from_time
            FROM observations
            WHERE sampling_point_id = ANY(%(sp_ids)s)
              AND from_time >= %(min_time)s
              AND to_time <= %(max_time)s
              AND observationverification_id = 1
            LIMIT 1
            """,
            {"sp_ids": all_sp_ids, "min_time": min_time, "max_time": max_time},
        )
        approved = cursor.fetchone()
        if approved:
            raise Exception(
                f"Import blocked: verified (approved) data already exists for {approved[0]} at {approved[1]}. "
                "Verified data cannot be overwritten."
            )

        # Check to see if timestep matches with the imported values. Ignore if timestep is -1
        df_errors = df_values[(((df_values.to_time - df_values.from_time) / pd.Timedelta(seconds=1)).astype('int64') - ((df_values.apply(lambda x: U.actual_timestep(x.from_time, x.ts_timestep), axis=1))).astype('int64')) > 0]
        df_errors = df_errors[df_errors.ts_timestep != -1]
        if len(df_errors) > 0:
            l = len(df_errors)
            f = df_errors.iloc[0]
            raise Exception(f"Imported values does not match timestep. First error is at {f.sampling_point_id} {f.from_time} {f.to_time} {f.ts_timestep}")

        # Check timezone only if timestamps are tz-aware (user provided timezone info)
        if df_values["from_time"].dt.tz is not None:
            expected_offset_minutes = Common.get_settings_timezone(cursor)
            actual_offsets = df_values["from_time"].apply(lambda t: t.utcoffset().total_seconds() / 60).unique()
            if len(actual_offsets) > 1:
                raise Exception("Imported data contains multiple timezones. All timestamps must have the same timezone.")
            if len(actual_offsets) > 0 and actual_offsets[0] != expected_offset_minutes:
                def offset_to_tz_string(offset_minutes):
                    if offset_minutes == 0:
                        return "UTC"
                    hours = int(offset_minutes / 60)
                    return f"UTC{hours:+03d}"

                expected_tz = offset_to_tz_string(expected_offset_minutes)
                actual_tz = offset_to_tz_string(actual_offsets[0])
                raise Exception(f"Imported data timezone ({actual_tz}) does not match configured timezone ({expected_tz}). Please check your data or update settings.")

            # Strip timezone after validation - database stores tz-naive timestamps
            df_values["from_time"] = df_values["from_time"].dt.tz_localize(None)
            df_values["to_time"] = df_values["to_time"].dt.tz_localize(None)

        printcol(f"- Verifying values took {time.perf_counter() - bench} seconds")

    @staticmethod
    def post_import_calculate(cursor: any, sp_ids: list, from_time, to_time):
        """Post-commit recalculation for calculated series.
        Handles the race condition where primary and secondary SPs are imported
        concurrently and neither can see the other's uncommitted data during calculate().
        Called in a fresh transaction after the main import commits."""
        cursor.execute("""
            SELECT * FROM calculated_series
            WHERE "primary" = ANY(%(ids)s) OR secondary = ANY(%(ids)s)
        """, {"ids": sp_ids})
        series = cursor.fetchall()
        if not series:
            return

        partner_ids = list({row["primary"] for row in series} | {row["secondary"] for row in series})
        result_ids = [row["result"] for row in series]

        cursor.execute("""
            SELECT o.sampling_point_id,
                   o.from_time, o.to_time,
                   COALESCE(o.scaled_value, o.value) AS value,
                   COALESCE(o.scaled_value, o.value) AS import_value,
                   COALESCE(o.scaled_value, o.value) AS scaled_value,
                   o.observationverification_id,
                   o.observationvalidity_id
            FROM observations o
            WHERE o.sampling_point_id = ANY(%(ids)s)
              AND o.from_time >= %(from_time)s
              AND o.to_time <= %(to_time)s
        """, {"ids": partner_ids, "from_time": from_time, "to_time": to_time})
        rows = cursor.fetchall()
        if not rows:
            return

        df = pd.DataFrame([dict(r) for r in rows])
        df = Common.add_timeserie_info(cursor, df)
        df = df[df["has_timeserie_info"] == True].copy()
        if df.empty:
            return

        df = Importing.process_scaled_values(cursor, df)

        df_result = df[df["sampling_point_id"].isin(result_ids)].copy()
        if df_result.empty:
            return

        Importing.upsert(cursor, df_result)
        printcol(f"- Post-import calculate: upserted {len(df_result)} rows for {result_ids}")

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
            INSERT INTO observations (sampling_point_id, from_time, to_time, value, observationverification_id, observationvalidity_id, import_value, scaled_value, touched)
            SELECT s.sampling_point_id, s.from_time, s.to_time, s.value, s.observationverification_id, s.observationvalidity_id, s.import_value, s.scaled_value, now()
            FROM source s
            WHERE NOT EXISTS (
                SELECT 1
                FROM updates u
                WHERE u.sampling_point_id = s.sampling_point_id
                AND u.from_time = s.from_time
                AND u.to_time = s.to_time
            )
        """

        d = Importing.__data2io__(df_values)
        cols = ('sampling_point_id', 'from_time', 'to_time', 'value', 'observationverification_id', 'observationvalidity_id', 'import_value', 'scaled_value')
        cursor.execute('CREATE TEMP TABLE source(sampling_point_id varchar(100), from_time timestamp, to_time timestamp, value numeric(255,5), observationverification_id integer, observationvalidity_id integer, import_value numeric(255,5), scaled_value numeric(255,5)) ON COMMIT DROP;')
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
