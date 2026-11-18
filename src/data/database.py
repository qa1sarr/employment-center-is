"""SQL Server-мен жұмыс: қосылу, сұраныс орындау, транзакция (pyodbc)."""
from contextlib import closing, contextmanager


def _rows(cur) -> list:
    columns = [c[0] for c in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


class Transaction:
    """Бір қосылым ішіндегі сұраныстар. Транзакцияны Database басқарады."""

    def __init__(self, conn):
        self.conn = conn

    def query(self, sql: str, params: tuple = ()) -> list:
        """SELECT: жолдар тізімін dict ретінде қайтарады."""
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return _rows(cur)

    def execute(self, sql: str, params: tuple = (), returns_id: bool = False):
        """INSERT/UPDATE/DELETE. returns_id=True болса, OUTPUT INSERTED.* мәнін қайтарады."""
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()[0] if returns_id else None


class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def _connect(self):
        import pyodbc  # бағдарлама тек осы жерде pyodbc-ты қолданады
        return pyodbc.connect(self.connection_string)

    def query(self, sql: str, params: tuple = ()) -> list:
        with closing(self._connect()) as conn:
            return Transaction(conn).query(sql, params)

    def execute(self, sql: str, params: tuple = (), returns_id: bool = False):
        with closing(self._connect()) as conn:
            result = Transaction(conn).execute(sql, params, returns_id)
            conn.commit()
            return result

    @contextmanager
    def transaction(self):
        """Бірнеше сұранысты бір транзакцияда орындау: қате болса, бәрі қайтарылады."""
        with closing(self._connect()) as conn:
            try:
                yield Transaction(conn)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
