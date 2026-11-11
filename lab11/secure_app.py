# secure_app.py — қауіпсіз іздеу бағдарламасы (параметрленген сұраныс)
from lab11.db_setup import create_demo_db
from lab11.secure_search import search_secure

conn = create_demo_db()
title = input("Вакансия атауын енгізіңіз: ")

try:
    query, rows = search_secure(conn, title)
    print("SQL сұранысы:")
    print(query)
    print("Параметр:", repr("%" + title + "%"))
    print("Табылған жазба саны:", len(rows))
    for row in rows:
        print(row)
except Exception as e:
    print("Қате:", type(e).__name__, "-", e)
conn.close()
