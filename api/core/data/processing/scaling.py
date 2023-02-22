from pandas import DataFrame
import pandas as pd
import time
import numpy as np
from core.printcol import printcol
from core.data.processing.common import Common


class Scaling:

    @staticmethod
    def Scale(cursor: any, df_values: DataFrame, scalingpoint=None):
        bench = time.perf_counter()
        grouped_values = df_values.groupby("sampling_point_id")
        for key, group in grouped_values:
            scaling_points = Scaling.__scalingpoints__(cursor, key, scalingpoint)
            if len(scaling_points) > 0:
                for sp in scaling_points:
                    filtered_values = []
                    if sp["f_sampling_point_id"] is not None and sp["t_sampling_point_id"] is not None:
                        filtered_values = group[(group["end_position"].apply(lambda t: t.timestamp()) >= sp["f_timestamp"].timestamp()) & (group["end_position"].apply(lambda t: t.timestamp()) < sp["t_timestamp"].timestamp())]

                        for row in filtered_values.itertuples():
                            scaled_value = Scaling.__scale__(sp["f_zero_point"], sp["f_span_value"], sp["f_gas_concentration"], sp["f_timestamp"].timestamp(), sp["t_zero_point"], sp["t_span_value"], sp["t_gas_concentration"], sp["t_timestamp"].timestamp(), row.value, row.end_position.timestamp())
                            df_values.at[row.Index,  "value"] = scaled_value
                            df_values.at[row.Index,  "scaled_value"] = scaled_value

                    elif sp["f_sampling_point_id"] is not None:
                        filtered_values = group[(group["end_position"].apply(lambda t: t.timestamp()) >= sp["f_timestamp"].timestamp())]

                        for row in filtered_values.itertuples():
                            scaled_value = Scaling.__scalevalue__(sp["f_zero_point"], sp["f_span_value"], sp["f_gas_concentration"], row.value)
                            df_values.at[row.Index,  "value"] = scaled_value
                            df_values.at[row.Index,  "scaled_value"] = scaled_value

                    elif sp["t_sampling_point_id"] is not None:
                        filtered_values = group[(group["end_position"].apply(lambda t: t.timestamp()) < sp["t_timestamp"].timestamp())]

                        for row in filtered_values.itertuples():
                            scaled_value = Scaling.__scalevalue__(sp["t_zero_point"], sp["t_span_value"], sp["t_gas_concentration"], row.value)
                            df_values.at[row.Index,  "value"] = scaled_value
                            df_values.at[row.Index,  "scaled_value"] = scaled_value

        printcol(f"- Scaling took {time.perf_counter() - bench} seconds")
        return df_values

    @staticmethod
    def ReScale(cursor, use_scalingpoint, sampling_point_id, zero, span, gas, timestamp, old_timestamp=None):
        minmax = Scaling.__minmax__(cursor, sampling_point_id, timestamp, old_timestamp)
        df_values = Scaling.__get_imported_observations(cursor, sampling_point_id, minmax["min"], minmax["max"])
        Common.validate_dataframe(df_values)
        df_values = Common.add_timeserie_info(cursor, df_values)
        return Scaling.Scale(cursor, df_values, {"sampling_point_id": sampling_point_id, "zero_point": zero, "span_value": span, "gas_concentration": gas, "timestamp": timestamp, "old_timestamp": old_timestamp, "use_scalingpoint": use_scalingpoint})

    @staticmethod
    def __minmax__(cursor, sampling_point_id, timestamp, old_timestamp):
        sql = """
          select
              min(extract(epoch from f.timestamp)*1000) as min,
              max(extract(epoch from t.timestamp)*1000) as max
          from
          (
              select s.id, s.timestamp, lead(s.id) over (order by s.timestamp asc) as next
              from scaling_points s
              where sampling_point_id = %(sampling_point_id)s
              and s.timestamp < %(timestamp)s
              and s.timestamp <> %(old_timestamp)s
              order by s.timestamp desc
              limit 1
          ) f
          FULL OUTER JOIN
          (
                  select s.id, s.timestamp
                  from scaling_points s
                  where sampling_point_id = %(sampling_point_id)s
                  and s.timestamp > %(timestamp)s
                  and s.timestamp <> %(old_timestamp)s
                  order by s.timestamp asc
                  limit 1
          ) t ON t.id = f.next
          --order by t.timestamp, f.timestamp
        """
        cursor.execute(sql, {'sampling_point_id': sampling_point_id, 'timestamp': timestamp, 'old_timestamp': old_timestamp})
        minmax = cursor.fetchone()
        if minmax is None:
            return {"min": None, "max": None}
        return minmax

    @staticmethod
    def __get_imported_observations(cursor, sampling_point_id, min=None, max=None):
        sql = """
            select 
              o.id, 
              o.sampling_point_id, 
              o.begin_position, 
              o.end_position, 
              o.verification_flag, 
              o.validation_flag, 
              o.import_value::DOUBLE PRECISION, 
              o.import_value::DOUBLE PRECISION as value, 
              o.from_time, o.to_time, 
              extract(epoch from o.to_time)*1000 as to_epoch, 
              extract(epoch from o.from_time)*1000 as from_epoch
            from observations o 
            where o.sampling_point_id = %(sampling_point_id)s
        """

        if min != None:
            sql = sql + " and extract(epoch from o.to_time)*1000 >= %(min)s"

        if max != None:
            sql = sql + " and extract(epoch from o.to_time)*1000 < %(max)s"

        sql = sql + " order by o.to_time"

        cursor.execute(sql, {"sampling_point_id": sampling_point_id, "min": min, "max": max})
        values = cursor.fetchall()
        return pd.DataFrame(values)

    @staticmethod
    def __scalingpoints__(cursor: any, sampling_point_id: str, scalingpoint=None):
        with_sql = ""
        model = {'sampling_point_id': sampling_point_id}

        if scalingpoint is not None:
            if scalingpoint["use_scalingpoint"] == True:
                with_sql = """
                    with scaling_points as (
                        (select -1 as id, %(sampling_point_id)s as sampling_point_id, %(zero_point)s as zero_point, %(span_value)s as span_value, %(gas_concentration)s as gas_concentration, %(timestamp)s as timestamp, 'generated' as createdby)
                        union
                        select * from scaling_points where timestamp <> %(old_timestamp)s
                    )
                """
            elif scalingpoint["use_scalingpoint"] == False:
                with_sql = """
                    with scaling_points as (
                        select * from scaling_points where timestamp <> %(timestamp)s
                    )
                """

            model = scalingpoint
            model["sampling_point_id"] = sampling_point_id

        sql = """
            select
                f.sampling_point_id as f_sampling_point_id,
                f.zero_point as f_zero_point,
                f.span_value as f_span_value,
                f.gas_concentration as f_gas_concentration,
                f.timestamp as f_timestamp,
                --extract(epoch from f.timestamp) as f_timestamp_number,
                t.sampling_point_id as t_sampling_point_id,
                t.zero_point as t_zero_point,
                t.span_value as t_span_value,
                t.gas_concentration as t_gas_concentration,
                t.timestamp as t_timestamp--,
                --extract(epoch from t.timestamp) as t_timestamp_number

            from
            (
                select a.*, lead(a.id) over (order by a.timestamp asc) as next
                from scaling_points a
                where a.sampling_point_id = %(sampling_point_id)s
            ) f
            FULL OUTER JOIN
            (
                select a.*
                from scaling_points a
                where a.sampling_point_id = %(sampling_point_id)s
            ) t ON t.id = f.next
            order by t.timestamp, f.timestamp
        """
        cursor.execute(with_sql + sql, model)
        return cursor.fetchall()

    @staticmethod
    def __scale__(prev_zero, prev_span, prev_gas, prev_epoch, next_zero, next_span, next_gas, next_epoch, value, value_epoch):
        zero_diff = float(next_zero) - float(prev_zero)
        epoch_diff = float(next_epoch) - float(prev_epoch)
        epoch_value_diff = float(value_epoch) - float(prev_epoch)
        span_diff = float(next_span) - float(prev_span)

        zero = float(prev_zero) + (zero_diff / epoch_diff) * epoch_value_diff
        span = float(prev_span) + (span_diff / epoch_diff) * epoch_value_diff

        return Scaling.__scalevalue__(zero, span, float(prev_gas), float(value))

    @staticmethod
    def __scalevalue__(zero, span, gas, value):
        return (float(gas) / (float(span) - float(zero))) * (float(value) - float(zero))
