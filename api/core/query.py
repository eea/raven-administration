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
                from sampling_points sp
                join stations s on sp.station_id = s.id
                -- LEFT, not inner: pollutant_id, time_resolution_id and unit_id are all
                -- nullable since migration 012, for series whose component or unit has no
                -- EEA term (a local pollutant, or m/s and degC). Inner joins here dropped
                -- 2,177 of 3,580 production sampling points without a trace. CONCAT treats
                -- NULL as empty, so a partially-configured series gets a shorter label
                -- rather than vanishing from the picker.
                left join eea_pollutants p on sp.pollutant_id = p.id
                left join eea_times t on sp.time_resolution_id = t.id
                left join eea_concentrations u on sp.unit_id = u.id
                order by LOWER(s.name), LOWER(p.notation), LOWER(t.label)
            """)
            return cursor.fetchall()

    @staticmethod
    def timeseries_by_access():
        with CursorFromPool() as cursor:
            with_network_sql, n_param = Q.with_networks_by_access_as_sql()
            cursor.execute(f"""
                {with_network_sql}
                select CONCAT(s.name,', ', p.notation,', ', t.label, ', ', u.notation )  as label, sp.id as value
                from sampling_points sp
                join stations s on sp.station_id = s.id
                join network_access n on n.id = s.network_id
                -- LEFT: nullable measurement config, see Q.timeseries().
                left join eea_pollutants p on sp.pollutant_id = p.id
                left join eea_times t on sp.time_resolution_id = t.id
                left join eea_concentrations u on sp.unit_id = u.id
                order by LOWER(s.name), LOWER(p.notation), LOWER(t.label)
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
                      to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime,
                      aa.timestep_seconds
                  FROM
                 (
                  SELECT sp.id as sp, sp.id as value, s.name, COALESCE(NULLIF(po.notation, ''), po.label) as pollutant,  sp.from_time as fromtime, sp.to_time as totime, t.notation as timestep, t.timestep as timestep_seconds, u.notation as unit
                    FROM network_access n
                    JOIN stations s ON n.id = s.network_id
                    JOIN sampling_points sp ON s.id = sp.station_id
                    -- LEFT: nullable measurement config, see Q.timeseries().
                    LEFT JOIN eea_pollutants po ON sp.pollutant_id = po.id
                    LEFT JOIN eea_times t ON sp.time_resolution_id = t.id
                    LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
                    WHERE 1=1
                        and sp.from_time is not null
                        and sp.to_time is not null
                    GROUP by s.name, sp.id, sp.pollutant_id, COALESCE(NULLIF(po.notation, ''), po.label), sp.from_time,  sp.to_time, t.notation, t.timestep, u.notation
                ) aa
                order by LOWER(aa.name), aa.pollutant, aa.timestep
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
                      to_char(aa.totime, 'YYYY-MM-DD"T"HH24:MI:SS') as totime,
                      aa.equipment, aa.equipment_identifier
                  FROM
                (
                  SELECT sp.id as sp, sp.id as value, s.name, COALESCE(NULLIF(po.notation, ''), po.label) as pollutant,
                         sp.from_time as fromtime, sp.to_time as totime, t.notation as timestep, u.notation as unit,
                         lp.equipment, lp.equipment_identifier
                    FROM network_access n
                    JOIN stations s ON n.id = s.network_id
                    JOIN sampling_points sp ON s.id = sp.station_id
                    -- LEFT: nullable measurement config, see Q.timeseries().
                    LEFT JOIN eea_pollutants po ON sp.pollutant_id = po.id
                    LEFT JOIN eea_times t ON sp.time_resolution_id = t.id
                    LEFT JOIN eea_concentrations u ON sp.unit_id = u.id
                    LEFT JOIN (
                        SELECT DISTINCT ON (pr.sampling_point_id)
                            pr.sampling_point_id,
                            COALESCE(NULLIF(me.notation, ''), me.label) as equipment,
                            pr.equipment_identifier
                        FROM processes pr
                        LEFT JOIN eea_measurementequipments me ON pr.equipment_id = me.id
                        ORDER BY pr.sampling_point_id, pr.process_activity_begin DESC
                    ) lp ON lp.sampling_point_id = sp.id
                    WHERE sp.from_time is not null
                      AND sp.to_time is not null
                    GROUP by s.name, sp.id, sp.pollutant_id, COALESCE(NULLIF(po.notation, ''), po.label),
                             sp.from_time, sp.to_time, t.notation, u.notation, lp.equipment, lp.equipment_identifier
                ) aa
                order by LOWER(aa.name), LOWER(aa.pollutant), LOWER(aa.timestep)
            """, n_param)
            return cursor.fetchall()

    @staticmethod
    def timezones():
        with CursorFromPool() as cursor:
            cursor.execute("select r.notation as label, r.id as value from eea_timezones r order by LOWER(r.notation)")
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
            -- eea_pollutants was joined in here as `p.pollutant_id = po.id` without
            -- contributing a single column: this CTE only ever returns p.id. That made it
            -- an access filter by accident, and once migration 012 allowed a NULL
            -- pollutant_id it silently removed 591 of 3,580 sampling points from every
            -- caller — including the 581 that carry a local pollutant via the
            -- nilu-pollutants plugin. Access is a question about networks, not about
            -- whether a component happens to have an EEA vocabulary term.
            select p.id
            from stations s, sampling_points p, network_access n
            where 1=1
            and s.network_id = n.id
            and s.id = p.station_id
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

    @staticmethod
    def pollutants_lookup(exclude_ids=None):
        """Centralized pollutant lookup - uses notation if available, otherwise label"""
        with CursorFromPool() as cursor:
            exclude_clause = "WHERE id NOT IN %(exclude_ids)s" if exclude_ids else ""
            cursor.execute(f"""
                SELECT id as value, COALESCE(NULLIF(notation, ''), label) || ' (' || id || ')' as label 
                FROM eea_pollutants 
                {exclude_clause}
                ORDER BY LOWER(COALESCE(NULLIF(notation, ''), label))
            """, {"exclude_ids": tuple(exclude_ids)} if exclude_ids else {})
            return cursor.fetchall()
