# login_cli.py — консольдік нұсқа (терезе ашылмаса қолданылады).
# Іске қосу (репо түбірінен):  python -m lab11.login_cli
from lab11.db_setup import create_demo_db
from lab11.auth import login_vulnerable, login_secure
from lab11.vulnerable_search import search_vulnerable
from lab11.secure_search import search_secure


def main():
    conn = create_demo_db()
    print("1 - ОСАЛ режим, 2 - ҚАУІПСІЗ режим")
    secure = input("Режимді таңдаңыз (1/2): ").strip() == "2"
    login_fn = login_secure if secure else login_vulnerable
    search_fn = search_secure if secure else search_vulnerable

    email = input("Логин (email): ")
    password = input("Пароль: ")
    try:
        query, row = login_fn(conn, email, password)
    except Exception as e:
        print("Қате:", e)
        return
    print("SQL сұранысы:")
    print(query)
    if not row:
        print("Логин немесе пароль қате!")
        return
    print("Жүйеге кіру сәтті орындалды!")
    print("Пайдаланушы: %s (%s), рөлі: %s" % (row[1], row[2], row[3]))

    print("--- Интерфейс: вакансия іздеу (шығу үшін бос енгізіңіз) ---")
    while True:
        text = input("Вакансия атауы: ")
        if text == "":
            break
        try:
            q, rows = search_fn(conn, text)
        except Exception as e:
            print("Қате:", e)
            continue
        print("Табылған жазба саны:", len(rows))
        for r in rows:
            print(r)


if __name__ == "__main__":
    main()
