from api.core.database import CursorFromPool


class Q:
    @staticmethod
    def timeseries():
        with CursorFromPool() as cursor:
            cursor.execute("""
                select CONCAT(s.name,', ', p.notation,', ', t.label )  as label, sp.id as value
                from sampling_points sp, stations s, eea_pollutants p, eea_times t
                where sp.station_id = s.id
                and sp.pollutant = p.uri
                and sp.timestep = t.id
                order by s.name, p.notation, t.label
            """)
            return cursor.fetchall()

    @staticmethod
    def timezones():
        with CursorFromPool() as cursor:
            cursor.execute("select r.notation as label, r.id as value from eea_timezones r order by r.notation")
            return cursor.fetchall()
