"""UI -> логика -> деректер ағынын тексереді (HTTP сұраныс Flask test client арқылы)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app  # noqa: E402
from business.matching_service import MatchingService  # noqa: E402
from fakes import make_repos  # noqa: E402


class FlowTests(unittest.TestCase):
    def setUp(self):
        self.store, repos = make_repos()
        self.app = create_app(repos)
        self.client = self.app.test_client()

    def login(self, email, password="123456"):
        return self.client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    # --- авторизация модулі ---
    def test_login_ok_and_wrong_password(self):
        r = self.login("aigerim@mail.kz")
        self.assertIn("Вакансиялар", r.get_data(as_text=True))
        self.client.get("/logout")
        r = self.login("aigerim@mail.kz", "wrong")
        self.assertIn("Email немесе құпиясөз қате", r.get_data(as_text=True))

    def test_protected_page_redirects_to_login(self):
        r = self.client.get("/vacancies")
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers["Location"].endswith("/login"))

    # --- өтінім беру: негізгі ағын UI -> Service -> Repository ---
    def test_apply_full_flow(self):
        self.login("aigerim@mail.kz")
        r = self.client.post("/vacancies/1/apply", follow_redirects=True)
        text = r.get_data(as_text=True)
        self.assertIn("Өтінім қабылданды. Сәйкестік: 100.0%", text)
        # деректер деңгейіне жазылды
        self.assertEqual(len(self.store.applications), 1)
        self.assertEqual(self.store.matches[0]["score"], 100.0)
        # жұмыс берушіге хабарлама кетті
        self.assertEqual(self.store.notifications[0]["user_id"], 4)
        self.assertIn("Junior аналитик вакансиясына жаңа өтінім түсті", self.store.notifications[0]["message"])

    def test_apply_twice_is_rejected(self):
        self.login("aigerim@mail.kz")
        self.client.post("/vacancies/1/apply")
        r = self.client.post("/vacancies/1/apply", follow_redirects=True)
        self.assertIn("өтінім беріп қойғансыз", r.get_data(as_text=True))
        self.assertEqual(len(self.store.applications), 1)

    def test_apply_to_closed_vacancy_is_rejected(self):
        self.login("aigerim@mail.kz")
        r = self.client.post("/vacancies/2/apply", follow_redirects=True)
        self.assertIn("Вакансия жабық", r.get_data(as_text=True))
        self.assertEqual(self.store.applications, [])

    def test_employer_cannot_apply(self):
        self.login("bakyt@techno.kz")
        r = self.client.post("/vacancies/1/apply", follow_redirects=True)
        self.assertIn("рұқсатыңыз жоқ", r.get_data(as_text=True))

    # --- өтінім мәртебесі + хабарландыру ---
    def test_employer_accepts_application_and_seeker_is_notified(self):
        self.login("aigerim@mail.kz"); self.client.post("/vacancies/1/apply"); self.client.get("/logout")
        self.login("bakyt@techno.kz")
        r = self.client.post("/applications/1/status", data={"status": "accepted"}, follow_redirects=True)
        self.assertIn("Мәртебе өзгертілді", r.get_data(as_text=True))
        self.assertEqual(self.store.applications[0]["status"], "accepted")
        self.assertIn("қабылданды", self.store.notifications[-1]["message"])
        self.assertEqual(self.store.notifications[-1]["user_id"], 1)

    def test_other_employer_cannot_change_status(self):
        self.login("aigerim@mail.kz"); self.client.post("/vacancies/1/apply"); self.client.get("/logout")
        self.login("aliya@market.kz")
        r = self.client.post("/applications/1/status", data={"status": "accepted"}, follow_redirects=True)
        self.assertIn("жатпайды", r.get_data(as_text=True))
        self.assertEqual(self.store.applications[0]["status"], "submitted")

    def test_invalid_status_rejected(self):
        self.login("aigerim@mail.kz"); self.client.post("/vacancies/1/apply"); self.client.get("/logout")
        self.login("bakyt@techno.kz")
        r = self.client.post("/applications/1/status", data={"status": "hacked"}, follow_redirects=True)
        self.assertIn("Белгісіз мәртебе", r.get_data(as_text=True))

    # --- вакансиялар ---
    def test_search_and_applicant_count(self):
        self.login("aigerim@mail.kz"); self.client.post("/vacancies/1/apply")
        r = self.client.get("/vacancies?q=аналитик")
        text = r.get_data(as_text=True)
        self.assertIn("Junior аналитик", text)
        self.assertNotIn("Бухгалтер", text)

    def test_employer_publishes_and_validates(self):
        self.login("bakyt@techno.kz")
        self.client.post("/vacancies", data={"title": "QA", "requirements": "SQL", "salary": "330000"})
        self.assertEqual(self.store.vacancies[-1]["title"], "QA")
        r = self.client.post("/vacancies", data={"title": "", "requirements": "", "salary": "1"}, follow_redirects=True)
        self.assertIn("атауын көрсетіңіз", r.get_data(as_text=True))
        r = self.client.post("/vacancies", data={"title": "X", "requirements": "", "salary": "abc"}, follow_redirects=True)
        self.assertIn("Жалақы сан болуы керек", r.get_data(as_text=True))

    # --- курстар, есеп ---
    def test_enroll_course(self):
        self.login("aigerim@mail.kz")
        self.client.post("/courses/1/enroll")
        self.assertEqual(self.store.enrollments, [(1, 1)])
        r = self.client.post("/courses/1/enroll", follow_redirects=True)
        self.assertIn("жазылып қойғансыз", r.get_data(as_text=True))

    def test_report_only_for_specialist(self):
        self.login("aigerim@mail.kz")
        r = self.client.get("/reports", follow_redirects=True)
        self.assertIn("рұқсатыңыз жоқ", r.get_data(as_text=True))
        self.client.get("/logout")
        self.login("erlan@enbek.kz")
        r = self.client.get("/reports")
        self.assertIn("Вакансиялар бойынша есеп", r.get_data(as_text=True))

    # --- сәйкестендіру ---
    def test_matching_score(self):
        m = MatchingService()
        self.assertEqual(m.score("Python, SQL, Excel", "Python, SQL"), 100.0)
        self.assertEqual(m.score("Python", "Python, SQL"), 50.0)
        self.assertEqual(m.score("Excel", "Python, SQL"), 0.0)
        self.assertEqual(m.score("Python", ""), 0.0)


if __name__ == "__main__":
    unittest.main()
