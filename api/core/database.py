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


class NamedCursorFromPool:
    """A server-side cursor, for result sets too large to hold in the worker.

    A plain cursor buffers the whole result inside psycopg2 before the first row
    is available, so iterating it lazily saves nothing — the AQR3
    ObservationMeasurementResult export measured ~2.2 kB of RSS per row, which is
    gigabytes for a full reporting year and OOM-kills the pod.

    A named cursor leaves the rows on the database and fetches them in batches of
    `itersize`, so the worker's memory stays flat no matter how many rows there
    are. PostgreSQL requires a transaction for this, which pooled connections
    already are, and the cursor must be closed before the commit.
    """

    def __init__(self, name, itersize=5000):
        self.name = name
        self.itersize = itersize
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = Database.get_connection()
        self.cursor = self.connection.cursor(name=self.name,
                                             cursor_factory=RealDictCursor)
        self.cursor.itersize = self.itersize
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
