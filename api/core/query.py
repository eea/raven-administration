from core.database import CursorFromPool
from core.jwt_ext_custom import can_see_all_networks, get_networks
from pydantic import BaseModel
from typing import List, Union


class DeleteModel(BaseModel):
    ids: List[Union[str, int]]

    def __getitem__(self, key):
        return super().__getattribute__(key)


class Q:
    @staticmethod
    def timeseries():
        with CursorFromPool() as cursor:
            cursor.execute("""
                select CONCAT(s.name,', ', p.notation,', ', t.label, ', ', u.notation )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t, eea_concentrations u
                where sp.station_id = s.id
                and sp.pollutant = p.uri
                and sp.timestep = t.id
                and sp.concentration = u.id
                order by s.name, p.notation, t.label
            """)
            return cursor.fetchall()

    @staticmethod
    def timeseries_by_access():
        with CursorFromPool() as cursor:
            with_network_sql, n_param = Q.with_networks_by_access_as_sql()
            cursor.execute(f"""
                {with_network_sql}
                select CONCAT(s.name,', ', p.notation,', ', t.label, ', ', u.notation )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t, eea_concentrations u, network_access n
                where sp.station_id = s.id
                and n.id = s.network_id
                and sp.pollutant = p.uri
                and sp.timestep = t.id
                and sp.concentration = u.id
                order by s.name, p.notation, t.label
            """, n_param)
            return cursor.fetchall()

    @staticmethod
    def timeseries_with_time_by_access():
        with CursorFromPool() as cursor:
            with_network_sql, n_param = Q.with_networks_by_access_as_sql()
            cursor.execute(f"""
                {with_network_sql}
                SELECT
                  aa.value,
                  CONCAT(aa.name,', ', aa.pollutant,', ', aa.timestep, ', ', aa.unit ) as label,
                      to_char(aa.fromtime, 'YYYY-MM-DD"T"HH24:MI:SS') as fromtime,
                      to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime
                  FROM
                 (
                  SELECT sp.id as sp, sp.id as value, s.name, COALESCE(NULLIF(po.notation, ''), po.label) as pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.label as timestep, u.notation as unit
                    FROM
                        network_access n,
                        stations s,
                        sampling_points sp,
                        eea_pollutants po,
                        eea_times t,
                        eea_concentrations u
                    WHERE 1=1
                        and n.id = s.network_id
                        and s.id = sp.station_id
                        and sp.pollutant_id = po.id
                        and sp.time_resolution_id = t.id
                        and sp.unit_id = u.id
                        and sp.from_time is not null
                        and sp.to_time is not null
                    GROUP by s.name, sp.id, sp.pollutant_id, COALESCE(NULLIF(po.notation, ''), po.label), sp.from_time,  sp.to_time, t.label, u.notation
                ) aa
                order by label
            """, n_param)
            return cursor.fetchall()

    @staticmethod
    def timeseries_columns_with_time_by_access():
        with CursorFromPool() as cursor:
            with_network_sql, n_param = Q.with_networks_by_access_as_sql()
            cursor.execute(f"""
                {with_network_sql}
                SELECT aa.name as station, aa.pollutant, aa.timestep, aa.unit, aa.value as sampling_point_id,                   
                      to_char(aa.fromtime, 'YYYY-MM-DD"T"HH24:MI:SS') as fromtime,
                      to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime
                  FROM
                (
                  SELECT sp.id as sp, sp.id as value, s.name, COALESCE(NULLIF(po.notation, ''), po.label) as pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.label as timestep, u.notation as unit
                    FROM
                        network_access n,
                        stations s,
                        sampling_points sp,
                        eea_pollutants po,
                        eea_times t,
                        eea_concentrations u
                    WHERE 1=1
                        and n.id = s.network_id
                        and s.id = sp.station_id
                        and sp.pollutant_id = po.id
                        and sp.time_resolution_id = t.id
                        and sp.unit_id = u.id
                        and sp.from_time is not null
                        and sp.to_time is not null
                    GROUP by s.name, sp.id, sp.pollutant_id, COALESCE(NULLIF(po.notation, ''), po.label), sp.from_time,  sp.to_time, t.label, u.notation
                ) aa
                order by station, pollutant, timestep
            """, n_param)
            return cursor.fetchall()

    @staticmethod
    def timezones():
        with CursorFromPool() as cursor:
            cursor.execute("select r.notation as label, r.id as value from eea_timezones r order by r.notation")
            return cursor.fetchall()

    @staticmethod
    def with_networks_by_access_as_sql():

        sql = f"""
          with network_access as
          (
            select *
            from networks
            {"" if can_see_all_networks() else "where id in %(networkids)s"}
          )
        """
        return sql, {"networkids": tuple(get_networks())}

    @staticmethod
    def networks_by_access_as_sql():

        sql = f"""
          network_access as
          (        
            select *
            from networks
            {"" if can_see_all_networks() else "where id in %(networkids)s"}
          )
        """
        return sql, {"networkids": tuple(get_networks())}

    @staticmethod
    def with_sampling_points_by_networks_access():
        sql = f"""
          with network_access as
          (
            select *
            from networks
            {"" if can_see_all_networks() else "where id in %(networkids)s"}
          ),
          sampling_point_access as 
          (
            select p.id
            from stations s, sampling_points p,  eea_pollutants po, network_access n
            where 1=1
            and s.network_id = n.id
            and s.id = p.station_id
            and p.pollutant_id = po.id
          )
        """
        return sql, {"networkids": tuple(get_networks())}

    @staticmethod
    def sampling_point_ids_by_networks_access(sampling_point_ids: list):
        with CursorFromPool() as cursor:
            sql = f"""
              select array_agg(sp.id) as spid
              from sampling_points sp, stations s, networks n
              where sp.station_id = s.id
              and s.network_id = n.id
              and sp.id in %(sampling_point_ids)s
              {"" if can_see_all_networks() else "and n.id in %(networkids)s"}      
            """
            cursor.execute(sql, {"sampling_point_ids": tuple(sampling_point_ids), "networkids": tuple(get_networks())})
            row = cursor.fetchone()
            return [] if row["spid"] == None else tuple(row["spid"])

    @staticmethod
    def has_no_access(sampling_point_id):
        return len(Q.sampling_point_ids_by_networks_access([sampling_point_id])) == 0

    @staticmethod
    def any_has_no_access(sampling_point_ids):
        return len(Q.sampling_point_ids_by_networks_access(sampling_point_ids)) != len(sampling_point_ids)

    @staticmethod
    def delete(table: str, model: DeleteModel):
        with CursorFromPool() as cursor:
            return Q.delete_with_cursor(cursor, table, model)

    @staticmethod
    def delete_with_cursor(cursor: CursorFromPool, table: str, model: DeleteModel):
        sql = f"""delete from {table} where id in %(ids)s"""
        cursor.execute(sql, {"ids": tuple(model.ids)})
        return cursor.rowcount
