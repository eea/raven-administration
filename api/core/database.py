from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor


class Database:
    __connection_pool = None

    @classmethod
    def init_app(cls, app):
        dsn = app.config["DB_URI"]
        cls.__connection_pool = pool.ThreadedConnectionPool(1, 100, dsn)

    @classmethod
    def get_connection(cls):
        conn = cls.__connection_pool.getconn()
        # If the connection was dropped while idle (e.g. server timeout / firewall),
        # discard it and open a fresh one so the request doesn't crash.
        try:
            conn.cursor().execute("SELECT 1")
        except OperationalError:
            cls.__connection_pool.putconn(conn, close=True)
            conn = cls.__connection_pool.getconn()
        return conn

    @classmethod
    def return_connection(cls, connection):
        cls.__connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        cls.__connection_pool.closeall()


class CursorFromPool:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        return self.cursor

    def __exit__(self, ex_type, ex_value, ex_traceback):
        try:
            if ex_value is not None:
                self.connection.rollback()
            else:
                self.cursor.close()
                self.connection.commit()

            if Database.return_connection(self.connection):
                self.connection.close()
        except:
            pass
