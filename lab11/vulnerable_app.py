# vulnerable_app.py — осал іздеу бағдарламасы (input() арқылы)
from lab11.db_setup import create_demo_db
from lab11.vulnerable_search import search_vulnerable

conn = create_demo_db()
title = input("Вакансия атауын енгізіңіз: ")

try:
    query, rows = search_vulnerable(conn, title)
    print("SQL сұранысы:")
    print(query)
    print("Табылған жазба саны:", len(rows))
    for row in rows:
        print(row)
except Exception as e:
    print("Қате:", type(e).__name__, "-", e)
conn.close()
