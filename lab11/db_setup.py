# db_setup.py — оқу мақсатындағы уақытша SQLite базасы (жадта жасалады).
# Кесте құрылымы «Жұмыспен қамту орталығы» жобасынан алынған (vacancies, users).
import sqlite3

from lab11.auth import hash_password


def create_demo_db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE users (
            user_id       INTEGER PRIMARY KEY,
            full_name     TEXT NOT NULL,
            email         TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL
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

    # Демо-аккаунттар: aigerim@mail.kz / 123456, bakyt@techno.kz / 123456,
    # aidos@enbek.kz / admin123 (парольдер SHA-256 хэшімен сақталады)
    cur.executemany(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
        [
            ("Айгерім Нұрланова", "aigerim@mail.kz", hash_password("123456"), "job_seeker"),
            ("Бақыт Серіков", "bakyt@techno.kz", hash_password("123456"), "employer"),
            ("Айдос Әкімов", "aidos@enbek.kz", hash_password("admin123"), "admin"),
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
