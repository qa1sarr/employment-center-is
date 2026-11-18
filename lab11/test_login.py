import unittest

from lab11.db_setup import create_demo_db
from lab11.auth import login_vulnerable, login_secure

INJ_ADMIN = "aidos@enbek.kz' --"      # парольсіз админге кіру
INJ_OR = "' OR 1=1 --"                # кез келген пайдаланушы болып кіру


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.conn = create_demo_db()

    def tearDown(self):
        self.conn.close()

    # қалыпты кіру: екі нұсқа бірдей
    def test_valid_login_both(self):
        for fn in (login_vulnerable, login_secure):
            _, row = fn(self.conn, "aigerim@mail.kz", "123456")
            self.assertIsNotNone(row)
            self.assertEqual(row[2], "aigerim@mail.kz")

    def test_wrong_password_both(self):
        for fn in (login_vulnerable, login_secure):
            _, row = fn(self.conn, "aigerim@mail.kz", "99999")
            self.assertIsNone(row)

    # осал нұсқа бұзылады
    def test_vulnerable_admin_bypass(self):
        _, row = login_vulnerable(self.conn, INJ_ADMIN, "anything")
        self.assertIsNotNone(row)
        self.assertEqual(row[3], "admin")

    def test_vulnerable_or_bypass(self):
        _, row = login_vulnerable(self.conn, INJ_OR, "anything")
        self.assertIsNotNone(row)

    # қауіпсіз нұсқа бұзылмайды
    def test_secure_rejects_injections(self):
        for inj in (INJ_ADMIN, INJ_OR):
            _, row = login_secure(self.conn, inj, "anything")
            self.assertIsNone(row, inj)


if __name__ == "__main__":
    unittest.main()
