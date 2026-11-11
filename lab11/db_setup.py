# db_setup.py — оқу мақсатындағы уақытша SQLite базасы (жадта жасалады).
# Кесте құрылымы «Жұмыспен қамту орталығы» жобасынан алынған (vacancies, users).
import sqlite3


def create_demo_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE users (
            user_id       INTEGER PRIMARY KEY,
            full_name     TEXT NOT NULL,
            email         TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE vacancies (
            vacancy_id INTEGER PRIMARY KEY,
            title      TEXT NOT NULL,
            salary     INTEGER,
            status     TEXT NOT NULL CHECK (status IN ('open', 'closed'))
        )
    """)

    cur.executemany(
        "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
        [
            ("Айгерім Нұрланова", "aigerim@mail.kz", "hash_a1"),
            ("Бақыт Серіков", "bakyt@techno.kz", "hash_b1"),
            ("Айдос Әкімов", "aidos@enbek.kz", "hash_admin"),
        ],
    )
    cur.executemany(
        "INSERT INTO vacancies (title, salary, status) VALUES (?, ?, ?)",
        [
            ("Junior аналитик", 380000, "open"),
            ("Web-әзірлеуші", 440000, "open"),
            ("Тестілеуші (QA)", 363000, "open"),
            ("Құрылыс прорабы", 450000, "open"),
            ("Медбике", 280000, "open"),
            ("Логист", 310000, "open"),
            ("Бас бухгалтер (құпия)", 900000, "closed"),
            ("Қауіпсіздік бастығы (құпия)", 850000, "closed"),
            ("Аналитик-тексеруші (жабық)", 500000, "closed"),
        ],
    )
    conn.commit()
    return conn
