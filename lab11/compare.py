# compare.py — бірдей енгізулерді екі нұсқаға беріп, нәтижесін салыстырады.
from lab11.db_setup import create_demo_db
from lab11.vulnerable_search import search_vulnerable
from lab11.secure_search import search_secure

TESTS = [
    ("Қалыпты іздеу", "аналитик"),
    ("Жоқ атау", "космонавт"),
    ("OR 1=1 шабуылы", "%' OR 1=1 --"),
    ("UNION шабуылы (users кестесі)",
     "x' UNION SELECT user_id, email, 0, password_hash FROM users --"),
    ("Бірнеше команда (DROP TABLE)", "x'; DROP TABLE vacancies; --"),
]


def run(search, conn, text):
    try:
        query, rows = search(conn, text)
        return rows, None
    except Exception as e:  # осал нұсқа қате беруі мүмкін
        return [], "%s: %s" % (type(e).__name__, e)


def main():
    for name, text in TESTS:
        print("=" * 70)
        print("Тест:", name)
        print("Енгізілген мән:", text)
        for label, search in (("ОСАЛ", search_vulnerable), ("ҚАУІПСІЗ", search_secure)):
            conn = create_demo_db()  # әр тест үшін таза база
            rows, err = run(search, conn, text)
            print("--- %s нұсқа ---" % label)
            if err:
                print("Қате:", err)
            else:
                print("Табылған жазба саны:", len(rows))
                for r in rows:
                    print("  ", r)
            conn.close()


if __name__ == "__main__":
    main()
