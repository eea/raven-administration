from api.core.utils import U
from pandas import DataFrame
import time
from api.core.printcol import printcol
import pandas as pd


class Flagging:
    @staticmethod
    def flag(cursor: any, df_values: DataFrame):
        bench = time.perf_counter()
        ids = df_values.sampling_point_id.unique()
        series = Flagging.__autovalidated_series__(cursor, tuple(ids))

        # Find, if any, repeating value from db before and after first, last and gaps
        df_values = Flagging.__add_edge_values_from_db_if_any(cursor, df_values, series)

        for serie in series:
            serie_filter = (df_values.sampling_point_id == serie["sampling_point_id"])
            verification_filter = (df_values.verification_flag > 1)
            validation_filter = (df_values.validation_flag > 0)

            tmp = df_values.assign(consecutive=df_values[serie_filter].value.groupby(((df_values[serie_filter].value != df_values[serie_filter].value.shift().fillna(df_values[serie_filter].value)) | (df_values[serie_filter].end_position.diff().dt.total_seconds().fillna(0) > 3600)).cumsum()).transform('size')).query('consecutive > ' + str(serie['rep']))

            max_filter = verification_filter & serie_filter & validation_filter & (df_values.value > serie["max"])
            min_filter = verification_filter & serie_filter & validation_filter & (df_values.value < serie["min"])
            rep_filter = verification_filter & serie_filter & validation_filter & (df_values.index.isin(tmp.index))

            df_values.loc[max_filter, "validation_flag"] = -1
            df_values.loc[min_filter, "validation_flag"] = -1
            df_values.loc[rep_filter, "validation_flag"] = -1

        printcol(f"- Flagging took {time.perf_counter() - bench} seconds")

    @staticmethod
    def __autovalidated_series__(cursor: any, sampling_point_ids):
        sql = """
            select distinct v.min, v.max,v.rep, p.id as sampling_point_id, t.timestep
            from autovalidated_series v, sampling_points p, eea_times t
            where v.pollutant = p.pollutant
            and p.timestep = t.id
            and p.id in %(ids)s
            and v.enabled = true
        """
        cursor.execute(sql, {"ids": sampling_point_ids})
        return cursor.fetchall()

    @staticmethod
    def __get_value_from_db__(cursor: any, sampling_point_id, dt_from, value):
        sql = """
            select o.sampling_point_id, o.begin_position, o.end_position, o.value, o.verification_flag, o.validation_flag, o.import_value, o.scaled_value
            from observations o
            where o.sampling_point_id = %(id)s
            and extract(epoch from o.from_time) = %(dt_from)s
            and o.value = %(value)s
        """
        cursor.execute(sql, {"id": sampling_point_id, "dt_from": dt_from, "value": value})
        row = cursor.fetchone()
        if row != None:
            row["begin_position"] = pd.to_datetime(row["begin_position"], format="%Y-%m-%dT%H:%M:%S%Z")
            row["end_position"] = pd.to_datetime(row["end_position"], format="%Y-%m-%dT%H:%M:%S%Z")
        return row

    @staticmethod
    def __add_edge_values_from_db_if_any(cursor: any, df_values: DataFrame, series: list):
        df_values.sort_values(by=['sampling_point_id', 'begin_position'], inplace=True)
        edge_values = []
        for serie in series:
            df_serie = df_values[(df_values.sampling_point_id == serie["sampling_point_id"])]
            # Find repeating values before the first value and after the last value
            first = df_serie[["value", "begin_position", "end_position"]].iloc[0]
            last = df_serie[["value", "begin_position", "end_position"]].iloc[-1]
            edge_values = edge_values + Flagging.__find_before_and_after_db_values(cursor, serie["sampling_point_id"], serie["rep"], serie["timestep"], first, last)

            # Find repeating values before and after gaps
            gaps = df_serie[(df_serie.begin_position.diff().dt.total_seconds().fillna(0) > serie["timestep"])].index
            for i in gaps:
                first = df_serie[["value", "begin_position", "end_position"]].iloc[i]
                edge_values = edge_values + Flagging.__find_previous_db_values__(cursor, serie["sampling_point_id"], first.value, first.begin_position.timestamp()+U.tz_in_seconds(first.begin_position), serie["rep"], serie["timestep"])

        if len(edge_values) > 0:
            df_edge_values = pd.DataFrame(edge_values)
            # if a value from db exists in df_values, drop db value from list
            existing_idx = df_edge_values[df_edge_values[['sampling_point_id', 'begin_position',  'end_position']].isin(df_values[['sampling_point_id', 'begin_position',  'end_position']].to_dict(orient='list')).all(axis=1)].index
            df_edge_values = df_edge_values.drop(existing_idx)
            df_values = pd.concat([df_values, df_edge_values], axis=0)
            df_values = df_values.drop_duplicates()
            df_values = df_values.reset_index(drop=True)
            df_values.sort_values(by=['sampling_point_id', 'begin_position'], inplace=True)

        return df_values

    @staticmethod
    def __find_before_and_after_db_values(cursor: any, sampling_point_id, rep, timestep, first, last):
        # first
        dt_from = first.begin_position.timestamp()+U.tz_in_seconds(first.begin_position)
        value = first.value
        values_first = Flagging.__find_previous_db_values__(cursor, sampling_point_id, value, dt_from, rep, timestep)

        # last
        dt_from = last.begin_position.timestamp() + U.tz_in_seconds(last.begin_position)
        value = last.value
        values_last = Flagging.__find_next_db_values__(cursor, sampling_point_id, value, dt_from, rep, timestep)

        return values_first + values_last

    @staticmethod
    def __find_previous_db_values__(cursor: any, sampling_point_id, value, dt_from, rep, timestep):
        edge_values = []
        stop = False
        iterations = 0
        while (stop == False):
            dt_from = dt_from - timestep
            obs = Flagging.__get_value_from_db__(cursor,  sampling_point_id, dt_from, value)
            if obs == None:
                stop = True
            else:
                edge_values.append(obs)
                iterations = iterations+1
                if iterations > rep:
                    stop = True
        return edge_values

    @staticmethod
    def __find_next_db_values__(cursor: any, sampling_point_id, value, dt_from, rep, timestep=3600):
        edge_values = []
        stop = False
        iterations = 0
        while (stop == False):
            dt_from = dt_from + timestep
            obs = Flagging.__get_value_from_db__(cursor,  sampling_point_id, dt_from, value)
            if obs == None:
                stop = True
            else:
                edge_values.append(obs)
                iterations = iterations+1
                if iterations > rep:
                    stop = True
        return edge_values
