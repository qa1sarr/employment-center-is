# vulnerable_search.py — ОСАЛ нұсқа: SQL сұранысы мәтінді біріктіру арқылы құрылады.
# Бағдарлама тек ашық (open) вакансияларды атауы бойынша іздеуі керек.


def build_vulnerable_query(title):
    # ҚАТЕ: пайдаланушы енгізген мән SQL кодына тікелей қосылады
    return (
        "SELECT vacancy_id, title, salary, status FROM vacancies "
        "WHERE status = 'open' AND title LIKE '%" + title + "%'"
    )


def search_vulnerable(conn, title):
    query = build_vulnerable_query(title)
    rows = conn.cursor().execute(query).fetchall()
    return query, rows
