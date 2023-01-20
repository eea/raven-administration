from psycopg2 import pool
from psycopg2.extras import RealDictCursor


class Database:
    __connection_pool = None

    @classmethod
    def init_app(cls, app):
        dsn = app.config["DB_URI"]
        cls.__connection_pool = pool.ThreadedConnectionPool(1, 100, dsn)

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

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
        if ex_value is not None:
            self.connection.rollback()
        else:
            try:
                self.cursor.close()
                self.connection.commit()
            except:
                self.connection.rollback()

        Database.return_connection(self.connection)
