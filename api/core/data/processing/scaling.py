from pandas import DataFrame
import time

from api.core.printcol import printcol


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
                    if sp["f_oc_id"] is not None and sp["t_oc_id"] is not None:
                        filtered_values = group[group["end_position"].apply(lambda t: t.value) >= sp["f_timestamp_number"] and group["end_position"].apply(lambda t: t.value) < sp["f_timestamp_number"]]

                        # for fv in filtered_values:
                        #     scaled_value = Scaling.__scale__(sp["f_zero_point"], sp["f_span_value"], sp["f_gas_concentration"], sp["f_timestamp_number"], sp["t_zero_point"], sp["t_span_value"], sp["t_gas_concentration"], sp["t_timestamp_number"], float(fv["value"]), arrow.get(fv["end_position"]).timestamp*1000)
                        #     fv["import_value"] = fv["value"]
                        #     fv["value"] = scaled_value
        printcol(f"- Scaling took {time.perf_counter() - bench} seconds")

    @staticmethod
    def __scalingpoints__(cursor: any, sampling_point_id: str, scalingpoint=None):
        with_sql = ""
        model = {'sampling_point_id': sampling_point_id}

        if scalingpoint is not None:
            if scalingpoint["use_scalingpoint"] == True:
                with_sql = """
                    with scaling_points as (
                        (select -1 as id, %(oc_id)s as oc_id, %(zero_point)s as zero_point, %(span_value)s as span_value, %(gas_concentration)s as gas_concentration, %(timestamp)s as timestamp, 'generated' as createdby)
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
                f.oc_id as f_oc_id,
                f.zero_point as f_zero_point,
                f.span_value as f_span_value,
                f.gas_concentration as f_gas_concentration,
                f.timestamp as f_timestamp,
                extract(epoch from f.timestamp)*1000 as f_timestamp_number,
                t.oc_id as t_oc_id,
                t.zero_point as t_zero_point,
                t.span_value as t_span_value,
                t.gas_concentration as t_gas_concentration,
                t.timestamp as t_timestamp,
                extract(epoch from t.timestamp)*1000 as t_timestamp_number

            from
            (
                select a.*, lead(a.id) over (order by a.timestamp asc) as next
                from scaling_points a, observing_capabilities b
                where b.sampling_point_id = %(sampling_point_id)s
                and a.oc_id = b.id
            ) f
            FULL OUTER JOIN
            (
                select a.*
                from scaling_points a, observing_capabilities b
                where b.sampling_point_id = %(sampling_point_id)s
                and a.oc_id = b.id
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
