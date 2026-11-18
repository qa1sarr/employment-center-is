"""Бүкіл қолданбаны нақты seed деректерімен (SQLite) тексереміз: үш деңгей бірге жұмыс істейді."""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from app import build_sql_repositories, create_app  # noqa: E402
from sqlite_db import SqliteDatabase  # noqa: E402

ACCOUNTS = {"job_seeker": "aigerim@mail.kz", "employer": "bakyt@techno.kz",
            "specialist": "erlan@enbek.kz", "admin": "aidos@enbek.kz"}


def make_client(email=None, demo=False, password="123456", mode=None):
    db = SqliteDatabase()
    app = create_app(build_sql_repositories(db), demo=demo)
    app.config["TESTING"] = True
    client = app.test_client()
    if email:
        login(client, email, password, mode)
    return client, db


def token(client):
    client.get("/login")
    with client.session_transaction() as s:
        return s["csrf"]


def login(client, email, password="123456", mode=None):
    data = {"email": email, "password": password, "csrf_token": token(client)}
    if mode:
        data["mode"] = mode
    return client.post("/login", data=data)


def post(client, url, **data):
    with client.session_transaction() as s:
        data["csrf_token"] = s["csrf"]
    return client.post(url, data=data, follow_redirects=True)


def text(resp):
    return resp.get_data(as_text=True)


class AuthTests(unittest.TestCase):
    def test_anonymous_redirected(self):
        c, _ = make_client()
        for url in ("/dashboard", "/vacancies", "/users", "/reports"):
            self.assertEqual(c.get(url).status_code, 302, url)

    def test_login_ok_and_wrong(self):
        c, _ = make_client()
        self.assertEqual(login(c, "aigerim@mail.kz").status_code, 302)
        c2, _ = make_client()
        r = login(c2, "aigerim@mail.kz", "қате")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(c2.get("/dashboard").status_code, 302)

    def test_csrf_required(self):
        c, _ = make_client()
        self.assertEqual(c.post("/login", data={"email": "aigerim@mail.kz", "password": "123456"}).status_code, 400)

    def test_logout(self):
        c, _ = make_client("aigerim@mail.kz")
        c.get("/logout")
        self.assertEqual(c.get("/dashboard").status_code, 302)

    def test_injection_blocked_in_secure_mode(self):
        c, _ = make_client()
        r = login(c, "aidos@enbek.kz' --", "x")
        self.assertEqual(r.status_code, 200)
        r = login(c, "' OR 1=1 --", "x")
        self.assertEqual(c.get("/dashboard").status_code, 302)

    def test_demo_off_ignores_vulnerable_mode(self):
        c, _ = make_client(demo=False)
        login(c, "aidos@enbek.kz' --", "x", mode="vulnerable")
        self.assertEqual(c.get("/dashboard").status_code, 302)

    def test_demo_vulnerable_mode_injectable(self):
        c, _ = make_client(demo=True)
        r = login(c, "aidos@enbek.kz' --", "x", mode="vulnerable")
        self.assertEqual(r.status_code, 302)
        self.assertIn("Айдос", text(c.get("/dashboard")))
        self.assertIn("ОСАЛ", text(c.get("/dashboard")))

    def test_demo_secure_mode_blocks(self):
        c, _ = make_client(demo=True)
        login(c, "aidos@enbek.kz' --", "x", mode="secure")
        self.assertEqual(c.get("/dashboard").status_code, 302)

    def test_demo_normal_login_works(self):
        c, _ = make_client(demo=True)
        self.assertEqual(login(c, "aidos@enbek.kz", "123456", mode="vulnerable").status_code, 302)


class RenderTests(unittest.TestCase):
    """Әр рөл рұқсат етілген барлық бетті қателіксіз ашады."""
    PAGES = {
        "job_seeker": ["/dashboard", "/profile", "/vacancies", "/vacancies/1", "/applications", "/resume",
                       "/courses", "/notifications"],
        "employer": ["/dashboard", "/profile", "/vacancies", "/vacancies/new", "/vacancies/1", "/vacancies/1/edit",
                     "/applications", "/notifications"],
        "specialist": ["/dashboard", "/profile", "/vacancies", "/vacancies/1", "/applications", "/courses",
                       "/seekers", "/seekers/1", "/reports", "/notifications"],
        "admin": ["/dashboard", "/profile", "/vacancies", "/vacancies/1", "/vacancies/1/edit", "/applications",
                  "/courses", "/seekers", "/seekers/1", "/users", "/users/new", "/reports", "/notifications"],
    }

    def test_all_pages_all_roles(self):
        for role, pages in self.PAGES.items():
            c, _ = make_client(ACCOUNTS[role])
            for url in pages:
                r = c.get(url)
                self.assertEqual(r.status_code, 200, "%s %s" % (role, url))
                self.assertIn("<!doctype html>", text(r))

    def test_login_page_and_css(self):
        c, _ = make_client(demo=True)
        html = text(c.get("/login"))
        self.assertIn("ОСАЛ", html)
        self.assertEqual(c.get("/static/style.css").status_code, 200)
        c2, _ = make_client(demo=False)
        self.assertNotIn("ОСАЛ", text(c2.get("/login")))

    def test_menu_per_role(self):
        c, _ = make_client(ACCOUNTS["job_seeker"])
        html = text(c.get("/dashboard"))
        self.assertIn("Менің түйіндемем", html)
        self.assertNotIn("Пайдаланушылар", html)
        c, _ = make_client(ACCOUNTS["admin"])
        self.assertIn("Пайдаланушылар", text(c.get("/dashboard")))

    def test_filters_and_search(self):
        c, _ = make_client(ACCOUNTS["admin"])
        self.assertEqual(c.get("/vacancies?q=Python&status=open").status_code, 200)
        self.assertEqual(c.get("/users?role=employer").status_code, 200)
        self.assertEqual(c.get("/seekers?q=Python").status_code, 200)
        self.assertEqual(c.get("/vacancies?q=%27%20OR%201%3D1%20--").status_code, 200)

    def test_missing_pages(self):
        c, _ = make_client(ACCOUNTS["admin"])
        self.assertEqual(c.get("/vacancies/9999").status_code, 404)
        self.assertEqual(c.get("/seekers/9999").status_code, 404)
        self.assertEqual(c.get("/nope").status_code, 404)


class RbacTests(unittest.TestCase):
    DENIED = {
        "job_seeker": ["/users", "/reports", "/seekers", "/vacancies/new", "/vacancies/1/edit"],
        "employer": ["/users", "/reports", "/seekers", "/resume", "/courses/new"],
        "specialist": ["/users", "/vacancies/new", "/resume"],
        "admin": ["/vacancies/new", "/resume"],
    }

    def test_forbidden_pages(self):
        for role, urls in self.DENIED.items():
            c, _ = make_client(ACCOUNTS[role])
            for url in urls:
                self.assertIn(c.get(url).status_code, (403, 404), "%s %s" % (role, url))
        c, _ = make_client(ACCOUNTS["job_seeker"])
        self.assertEqual(c.get("/users").status_code, 403)

    def test_employer_cannot_touch_foreign_vacancy(self):
        c, db = make_client("aliya@market.kz")  # 1-вакансия Бақыттікі
        self.assertEqual(c.get("/vacancies/1").status_code, 403)
        self.assertEqual(c.get("/vacancies/1/edit").status_code, 403)
        post(c, "/vacancies/1/close")
        self.assertEqual(db.query("select status from vacancies where vacancy_id = 1")[0]["status"], "open")

    def test_employer_cannot_change_foreign_application(self):
        c, db = make_client("aliya@market.kz")
        app = db.query("select a.application_id, a.status from applications a join vacancies v on v.vacancy_id = a.vacancy_id where v.employer_id = 4")[0]
        post(c, "/applications/%d/status" % app["application_id"], status="accepted")
        now = db.query("select status from applications where application_id = ?", (app["application_id"],))[0]["status"]
        self.assertEqual(now, app["status"])

    def test_post_without_role_denied(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        before = db.query("select count(*) n from users")[0]["n"]
        post(c, "/users", full_name="X", email="x@x.kz", password="123456", role="admin")
        self.assertEqual(db.query("select count(*) n from users")[0]["n"], before)
        post(c, "/courses", name="Hack", duration_hours="5")
        self.assertEqual(db.query("select count(*) n from courses where name='Hack'")[0]["n"], 0)
        post(c, "/courses/1/delete")
        self.assertEqual(db.query("select count(*) n from courses where course_id=1")[0]["n"], 1)

    def test_seeker_sees_only_own_applications(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        html = text(c.get("/applications"))
        mine = db.query("select count(*) n from applications where seeker_id = 1")[0]["n"]
        self.assertEqual(html.count('class="badge b-') , mine)

    def test_seeker_sees_only_open_vacancies(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        closed = db.query("select title from vacancies where status = 'closed'")
        html = text(c.get("/vacancies"))
        for row in closed:
            self.assertNotIn(row["title"], html)


class FlowTests(unittest.TestCase):
    def test_apply_creates_application_and_notifies_employer(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        vid = db.query("select vacancy_id from vacancies where status='open' and vacancy_id not in (select vacancy_id from applications where seeker_id=1) limit 1")[0]["vacancy_id"]
        emp = db.query("select employer_id from vacancies where vacancy_id=?", (vid,))[0]["employer_id"]
        n_before = db.query("select count(*) n from notifications where user_id=?", (emp,))[0]["n"]
        r = post(c, "/vacancies/%d/apply" % vid)
        self.assertIn("Өтінім қабылданды", text(r))
        self.assertEqual(db.query("select count(*) n from applications where seeker_id=1 and vacancy_id=?", (vid,))[0]["n"], 1)
        self.assertEqual(db.query("select count(*) n from notifications where user_id=?", (emp,))[0]["n"], n_before + 1)
        self.assertEqual(db.query("select count(*) n from match_results")[0]["n"] >= 1, True)
        r = post(c, "/vacancies/%d/apply" % vid)
        self.assertEqual(db.query("select count(*) n from applications where seeker_id=1 and vacancy_id=?", (vid,))[0]["n"], 1)

    def test_apply_to_closed_or_missing(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        closed = db.query("select vacancy_id from vacancies where status='closed'")
        if closed:
            before = db.query("select count(*) n from applications")[0]["n"]
            post(c, "/vacancies/%d/apply" % closed[0]["vacancy_id"])
            self.assertEqual(db.query("select count(*) n from applications")[0]["n"], before)
        self.assertEqual(post(c, "/vacancies/9999/apply").status_code, 200)

    def test_employer_changes_status_and_seeker_notified(self):
        c, db = make_client(ACCOUNTS["employer"])
        a = db.query("select a.application_id, a.seeker_id from applications a join vacancies v on v.vacancy_id=a.vacancy_id where v.employer_id=4 and a.status='submitted' limit 1")
        a = a[0] if a else db.query("select a.application_id, a.seeker_id from applications a join vacancies v on v.vacancy_id=a.vacancy_id where v.employer_id=4 limit 1")[0]
        n = db.query("select count(*) n from notifications where user_id=?", (a["seeker_id"],))[0]["n"]
        post(c, "/applications/%d/status" % a["application_id"], status="rejected")
        self.assertEqual(db.query("select status from applications where application_id=?", (a["application_id"],))[0]["status"], "rejected")
        self.assertEqual(db.query("select count(*) n from notifications where user_id=?", (a["seeker_id"],))[0]["n"], n + 1)
        post(c, "/applications/%d/status" % a["application_id"], status="hacked")
        self.assertEqual(db.query("select status from applications where application_id=?", (a["application_id"],))[0]["status"], "rejected")

    def test_employer_publish_edit_close_reopen(self):
        c, db = make_client(ACCOUNTS["employer"])
        r = post(c, "/vacancies", title="Тест вакансия", requirements="Python", salary="123456")
        self.assertIn("Вакансия жарияланды", text(r))
        vid = db.query("select max(vacancy_id) m from vacancies")[0]["m"]
        post(c, "/vacancies/%d/edit" % vid, title="Жаңа атау", requirements="SQL", salary="500000")
        self.assertEqual(db.query("select title, salary from vacancies where vacancy_id=?", (vid,))[0]["title"], "Жаңа атау")
        post(c, "/vacancies/%d/close" % vid)
        self.assertEqual(db.query("select status from vacancies where vacancy_id=?", (vid,))[0]["status"], "closed")
        post(c, "/vacancies/%d/reopen" % vid)
        self.assertEqual(db.query("select status from vacancies where vacancy_id=?", (vid,))[0]["status"], "open")

    def test_vacancy_validation(self):
        c, db = make_client(ACCOUNTS["employer"])
        n = db.query("select count(*) n from vacancies")[0]["n"]
        r = c.post("/vacancies", data={"title": "", "salary": "abc", "csrf_token": token(c)})
        self.assertEqual(r.status_code, 400)
        r = post(c, "/vacancies", title="X", requirements="", salary="-5")
        self.assertEqual(db.query("select count(*) n from vacancies")[0]["n"], n)

    def test_resume_save_creates_and_updates(self):
        c, db = make_client("zhasulan@mail.kz")
        post(c, "/resume", skills="Python, SQL", experience_years="3", experience="Әзірлеуші", education="Жоғары")
        row = db.query("select skills, experience_years from resumes where seeker_id=12")[0]
        self.assertEqual((row["skills"], row["experience_years"]), ("Python, SQL", 3))
        post(c, "/resume", skills="Go", experience_years="4", experience="", education="Жоғары")
        self.assertEqual(db.query("select count(*) n from resumes where seeker_id=12")[0]["n"], 1)
        self.assertEqual(db.query("select skills from job_seekers where user_id=12")[0]["skills"], "Go")

    def test_resume_validation(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        r = c.post("/resume", data={"skills": "", "experience_years": "-1", "csrf_token": token(c)})
        self.assertEqual(r.status_code, 400)

    def test_enroll(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        free = db.query("select course_id from courses where course_id not in (select course_id from enrollments where seeker_id=1) limit 1")[0]["course_id"]
        post(c, "/courses/%d/enroll" % free)
        self.assertEqual(db.query("select count(*) n from enrollments where seeker_id=1 and course_id=?", (free,))[0]["n"], 1)
        post(c, "/courses/%d/enroll" % free)  # қайталау — қате емес, дубликат жоқ
        self.assertEqual(db.query("select count(*) n from enrollments where seeker_id=1 and course_id=?", (free,))[0]["n"], 1)

    def test_specialist_assign_course(self):
        c, db = make_client(ACCOUNTS["specialist"])
        free = db.query("select course_id from courses where course_id not in (select course_id from enrollments where seeker_id=3) limit 1")[0]["course_id"]
        n = db.query("select count(*) n from notifications where user_id=3")[0]["n"]
        post(c, "/seekers/3/assign", course_id=str(free))
        row = db.query("select assigned_by from enrollments where seeker_id=3 and course_id=?", (free,))[0]
        self.assertEqual(row["assigned_by"], 6)
        self.assertEqual(db.query("select count(*) n from notifications where user_id=3")[0]["n"], n + 1)

    def test_admin_assign_has_no_assigner(self):
        c, db = make_client(ACCOUNTS["admin"])
        free = db.query("select course_id from courses where course_id not in (select course_id from enrollments where seeker_id=3) limit 1")[0]["course_id"]
        post(c, "/seekers/3/assign", course_id=str(free))
        self.assertIsNone(db.query("select assigned_by from enrollments where seeker_id=3 and course_id=?", (free,))[0]["assigned_by"])

    def test_course_create_and_admin_delete(self):
        c, db = make_client(ACCOUNTS["admin"])
        post(c, "/courses", name="Жаңа курс", description="Сипаттама", duration_hours="40")
        cid = db.query("select course_id from courses where name='Жаңа курс'")[0]["course_id"]
        post(c, "/courses/%d/delete" % cid)
        self.assertEqual(db.query("select count(*) n from courses where course_id=?", (cid,))[0]["n"], 0)
        c2, _ = make_client(ACCOUNTS["specialist"])
        post(c2, "/courses", name="Маман курсы", duration_hours="10")

    def test_admin_create_user_each_role_and_login(self):
        c, db = make_client(ACCOUNTS["admin"])
        cases = [("job_seeker", {"education": "Жоғары", "skills": "SQL"}), ("employer", {"company_name": "ТОО Тест", "industry": "IT"}),
                 ("specialist", {"department": "Бөлім"}), ("admin", {"access_level": "2"})]
        for i, (role, extra) in enumerate(cases):
            email = "new%d@test.kz" % i
            post(c, "/users", full_name="Жаңа %d" % i, email=email, phone="", password="secret1", role=role, **extra)
            self.assertEqual(db.query("select role from users where email=?", (email,))[0]["role"], role)
            c2, _ = make_client()
            c2.application = c.application
            c3 = c.application.test_client()
            self.assertEqual(login(c3, email, "secret1").status_code, 302)
        post(c, "/users", full_name="Дубль", email="new0@test.kz", password="secret1", role="job_seeker")
        self.assertEqual(db.query("select count(*) n from users where email='new0@test.kz'")[0]["n"], 1)
        post(c, "/users", full_name="Қысқа", email="short@test.kz", password="1", role="job_seeker")
        self.assertEqual(db.query("select count(*) n from users where email='short@test.kz'")[0]["n"], 0)
        post(c, "/users", full_name="Комп", email="nc@test.kz", password="secret1", role="employer")
        self.assertEqual(db.query("select count(*) n from users where email='nc@test.kz'")[0]["n"], 0)

    def test_admin_reset_password(self):
        c, db = make_client(ACCOUNTS["admin"])
        post(c, "/users/1/password", new="newpass1")
        self.assertEqual(login(c.application.test_client(), "aigerim@mail.kz", "newpass1").status_code, 302)

    def test_change_own_password(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        post(c, "/profile/password", current="қате", new="abcdef", repeat="abcdef")
        self.assertEqual(login(c.application.test_client(), "aigerim@mail.kz", "123456").status_code, 302)
        post(c, "/profile/password", current="123456", new="abcdef", repeat="abcdef")
        self.assertEqual(login(c.application.test_client(), "aigerim@mail.kz", "abcdef").status_code, 302)
        self.assertEqual(login(c.application.test_client(), "aigerim@mail.kz", "123456").status_code, 200)
        post(c, "/profile/password", current="abcdef", new="abcdef", repeat="zzzzzz")
        self.assertEqual(login(c.application.test_client(), "aigerim@mail.kz", "abcdef").status_code, 302)

    def test_update_profile(self):
        c, db = make_client(ACCOUNTS["job_seeker"])
        post(c, "/profile", full_name="Айгерім Жаңа", phone="+7000")
        self.assertEqual(db.query("select full_name, phone from users where user_id=1")[0]["phone"], "+7000")
        self.assertIn("Айгерім Жаңа", text(c.get("/dashboard")))

    def test_dashboard_numbers_match_database(self):
        c, db = make_client(ACCOUNTS["admin"])
        html = text(c.get("/dashboard"))
        users = db.query("select count(*) n from users")[0]["n"]
        self.assertIn('<div class="val">%d</div>' % users, html)

    def test_report_matches_database(self):
        c, db = make_client(ACCOUNTS["specialist"])
        html = text(c.get("/reports"))
        hired = db.query("select count(*) n from applications where status='accepted'")[0]["n"]
        self.assertIn('<div class="val">%d</div><div class="lbl">Жұмысқа алынды' % hired, html)

    def test_xss_escaped(self):
        c, db = make_client(ACCOUNTS["employer"])
        post(c, "/vacancies", title="<script>alert(1)</script>", requirements="x", salary="1")
        html = text(c.get("/vacancies"))
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_foreign_referrer_not_followed(self):
        c, db = make_client(ACCOUNTS["employer"])
        with c.session_transaction() as s:
            t = s["csrf"]
        r = c.post("/vacancies/9999/close", data={"csrf_token": t}, headers={"Referer": "http://evil.example/x"})
        self.assertNotIn("evil.example", r.headers.get("Location", ""))


if __name__ == "__main__":
    unittest.main()


class ForcedModeTests(unittest.TestCase):
    def _client(self, mode):
        db = SqliteDatabase()
        app = create_app(build_sql_repositories(db), demo=(mode == "vulnerable"), forced_mode=mode)
        app.config["TESTING"] = True
        return app.test_client()

    def test_vulnerable_file_any_password(self):
        c = self._client("vulnerable")
        self.assertEqual(login(c, "aidos@enbek.kz' --", "кез келген").status_code, 302)
        c = self._client("vulnerable")
        self.assertEqual(login(c, "' OR 1=1 --", "x").status_code, 302)
        c = self._client("vulnerable")
        self.assertEqual(login(c, "aidos@enbek.kz", "қате").status_code, 200)  # қарапайым қате пароль өтпейді
        self.assertNotIn('value="secure"', text(c.get("/login")))

    def test_secure_file_blocks(self):
        c = self._client("secure")
        login(c, "aidos@enbek.kz' --", "x", mode="vulnerable")  # жасырын өріс жіберсе де еленбейді
        self.assertEqual(c.get("/dashboard").status_code, 302)
        login(c, "' OR 1=1 --", "x")
        self.assertEqual(c.get("/dashboard").status_code, 302)
