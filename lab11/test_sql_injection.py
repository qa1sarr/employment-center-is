import sqlite3
import unittest

from lab11.db_setup import create_demo_db
from lab11.vulnerable_search import search_vulnerable
from lab11.secure_search import search_secure

OR_ATTACK = "%' OR 1=1 --"
UNION_ATTACK = "x' UNION SELECT user_id, email, 0, password_hash FROM users --"


class SqlInjectionTests(unittest.TestCase):
    def setUp(self):
        self.conn = create_demo_db()

    def tearDown(self):
        self.conn.close()

    # --- қалыпты жұмыс: екі нұсқа бірдей нәтиже береді ---
    def test_normal_search_same_result(self):
        _, a = search_vulnerable(self.conn, "аналитик")
        _, b = search_secure(self.conn, "аналитик")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 1)

    def test_normal_search_hides_closed(self):
        _, rows = search_secure(self.conn, "құпия")
        self.assertEqual(rows, [])

    # --- осал нұсқа шабуылға беріледі ---
    def test_vulnerable_or_attack_leaks_closed_vacancies(self):
        _, rows = search_vulnerable(self.conn, OR_ATTACK)
        self.assertEqual(len(rows), 9)
        self.assertTrue(any(r[3] == "closed" for r in rows))

    def test_vulnerable_union_attack_leaks_users(self):
        _, rows = search_vulnerable(self.conn, UNION_ATTACK)
        emails = [r[1] for r in rows]
        self.assertIn("aidos@enbek.kz", emails)

    def test_vulnerable_multiple_statements_rejected_by_driver(self):
        # sqlite3 бір execute()-те бір ғана команда орындайды
        with self.assertRaises((sqlite3.Warning, sqlite3.ProgrammingError)):
            search_vulnerable(self.conn, "x'; DROP TABLE vacancies; --")

    # --- қауіпсіз нұсқа шабуылға берілмейді ---
    def test_secure_or_attack_returns_nothing(self):
        _, rows = search_secure(self.conn, OR_ATTACK)
        self.assertEqual(rows, [])

    def test_secure_union_attack_returns_nothing(self):
        _, rows = search_secure(self.conn, UNION_ATTACK)
        self.assertEqual(rows, [])

    def test_secure_drop_attack_is_harmless(self):
        _, rows = search_secure(self.conn, "x'; DROP TABLE vacancies; --")
        self.assertEqual(rows, [])
        count = self.conn.execute("SELECT COUNT(*) FROM vacancies").fetchone()[0]
        self.assertEqual(count, 9)  # кесте сақталды

    def test_secure_never_returns_closed(self):
        for text in ["", "%", "'", OR_ATTACK, UNION_ATTACK]:
            _, rows = search_secure(self.conn, text)
            self.assertTrue(all(r[3] == "open" for r in rows), text)


if __name__ == "__main__":
    unittest.main()
