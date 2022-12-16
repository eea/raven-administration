from core.database import CursorFromPool
from core.jwt_ext_custom import can_see_all_networks, get_networks


class Access:
    @staticmethod
    def to_all_networks() -> bool:
        return can_see_all_networks()

    @staticmethod
    def to_network(network_id: str) -> bool:
        return True if can_see_all_networks() else network_id in get_networks()

    @staticmethod
    def to_station(station_id: str) -> bool:
        with CursorFromPool() as cursor:
            sql = f"""
              select 1
              from stations s, networks n
              where s.network_id = n.id
              and s.id = %(station_id)s
              {"" if can_see_all_networks() else "and n.id in %(networkids)s"}      
            """
            cursor.execute(sql, {"station_id": station_id, "networkids": tuple(get_networks())})
            row = cursor.fetchone()
            return row != None

    @staticmethod
    def to_sampling_point(sampling_point_id: str) -> bool:
        return Access.to_sampling_points([sampling_point_id])

    @staticmethod
    def to_sampling_points(sampling_point_ids: list) -> bool:
        ids = Access.only_sampling_points_ids_with_access(sampling_point_ids)
        return len(ids) > 0

    @staticmethod
    def to_observing_capability(observing_capability_id: str) -> bool:
        with CursorFromPool() as cursor:
            sql = f"""
              select 1
              from stations s, networks n, sampling_points p, observing_capabilities o
              where s.network_id = n.id
              and s.id = p.station_id
              and p.id = o.sampling_point_id
              and o.id = %(observing_capability_id)s
              {"" if can_see_all_networks() else "and n.id in %(networkids)s"}      
            """
            cursor.execute(sql, {"observing_capability_id": observing_capability_id, "networkids": tuple(get_networks())})
            row = cursor.fetchone()
            return row != None

    @staticmethod
    def only_sampling_points_ids_with_access(sampling_point_ids: list) -> list:
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
