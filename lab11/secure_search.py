# secure_search.py — ҚАУІПСІЗ нұсқа: параметрленген сұраныс (? белгісі).


SECURE_QUERY = (
    "SELECT vacancy_id, title, salary, status FROM vacancies "
    "WHERE status = 'open' AND title LIKE ?"
)


def search_secure(conn, title):
    # Енгізілген мән SQL коды емес, тек деректер ретінде беріледі
    rows = conn.cursor().execute(SECURE_QUERY, ("%" + title + "%",)).fetchall()
    return SECURE_QUERY, rows
