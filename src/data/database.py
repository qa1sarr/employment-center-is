"""SQL Server-мен жұмыс: қосылу, сұраныс орындау (pyodbc)."""
from contextlib import closing


class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def _connect(self):
        import pyodbc  # бағдарлама тек осы жерде pyodbc-ты қолданады
        return pyodbc.connect(self.connection_string)

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        """SELECT: жолдар тізімін dict ретінде қайтарады."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            columns = [c[0] for c in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def execute(self, sql: str, params: tuple = (), returns_id: bool = False):
        """INSERT/UPDATE/DELETE. returns_id=True болса, OUTPUT INSERTED.* мәнін қайтарады."""
        with closing(self._connect()) as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            new_id = cur.fetchone()[0] if returns_id else None
            conn.commit()
            return new_id
