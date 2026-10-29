"""Тесттерге арналған жалған (in-memory) репозиторийлер: SQL Server қажет емес."""
from business.auth_service import hash_password


class FakeStore:
    def __init__(self):
        pw = hash_password("123456")
        self.users = [
            {"user_id": 1, "full_name": "Айгерім", "email": "aigerim@mail.kz", "password_hash": pw, "role": "job_seeker"},
            {"user_id": 2, "full_name": "Данияр", "email": "daniyar@mail.kz", "password_hash": pw, "role": "job_seeker"},
            {"user_id": 4, "full_name": "Бақыт", "email": "bakyt@techno.kz", "password_hash": pw, "role": "employer"},
            {"user_id": 5, "full_name": "Алия", "email": "aliya@market.kz", "password_hash": pw, "role": "employer"},
            {"user_id": 6, "full_name": "Ерлан", "email": "erlan@enbek.kz", "password_hash": pw, "role": "specialist"},
        ]
        self.companies = {4: "Techno LLP", 5: "Market Plus"}
        self.vacancies = [
            {"vacancy_id": 1, "employer_id": 4, "title": "Junior аналитик", "requirements": "Python, SQL", "salary": 350000, "status": "open"},
            {"vacancy_id": 2, "employer_id": 5, "title": "Бухгалтер", "requirements": "Бухгалтерия, Excel", "salary": 300000, "status": "closed"},
        ]
        self.applications = []
        self.resumes = [{"resume_id": 1, "seeker_id": 1, "skills": "Python, SQL, Excel"}]
        self.matches = []
        self.courses = [{"course_id": 1, "name": "SQL негіздері", "description": "-", "duration_hours": 40}]
        self.enrollments = []
        self.notifications = []


class FakeUsers:
    def __init__(self, s): self.s = s
    def get_by_email(self, email):
        return next((u for u in self.s.users if u["email"].lower() == email.lower()), None)


class FakeVacancies:
    def __init__(self, s): self.s = s
    def list_with_counts(self, keyword=None):
        rows = []
        for v in self.s.vacancies:
            if keyword and keyword.lower() not in v["title"].lower():
                continue
            apps = [a for a in self.s.applications if a["vacancy_id"] == v["vacancy_id"]]
            rows.append({**v, "company": self.s.companies[v["employer_id"]],
                         "applicants": len(apps),
                         "hired": sum(1 for a in apps if a["status"] == "accepted")})
        return rows
    def get(self, vacancy_id):
        return next((v for v in self.s.vacancies if v["vacancy_id"] == vacancy_id), None)
    def create(self, employer_id, title, requirements, salary):
        vid = max(v["vacancy_id"] for v in self.s.vacancies) + 1
        self.s.vacancies.append({"vacancy_id": vid, "employer_id": employer_id, "title": title,
                                 "requirements": requirements, "salary": salary, "status": "open"})
        return vid
    def close(self, vacancy_id):
        self.get(vacancy_id)["status"] = "closed"


class FakeApplications:
    def __init__(self, s): self.s = s
    def exists(self, seeker_id, vacancy_id):
        return any(a["seeker_id"] == seeker_id and a["vacancy_id"] == vacancy_id for a in self.s.applications)
    def create(self, seeker_id, vacancy_id):
        aid = len(self.s.applications) + 1
        self.s.applications.append({"application_id": aid, "seeker_id": seeker_id,
                                    "vacancy_id": vacancy_id, "status": "submitted"})
        return aid
    def get(self, application_id):
        a = next((x for x in self.s.applications if x["application_id"] == application_id), None)
        if a is None:
            return None
        v = next(v for v in self.s.vacancies if v["vacancy_id"] == a["vacancy_id"])
        return {**a, "vacancy_title": v["title"], "employer_id": v["employer_id"]}
    def update_status(self, application_id, status):
        next(x for x in self.s.applications if x["application_id"] == application_id)["status"] = status
    def _rows(self, apps):
        rows = []
        for a in apps:
            v = next(v for v in self.s.vacancies if v["vacancy_id"] == a["vacancy_id"])
            u = next(u for u in self.s.users if u["user_id"] == a["seeker_id"])
            m = next((m for m in self.s.matches if m["vacancy_id"] == v["vacancy_id"]), None)
            rows.append({"application_id": a["application_id"], "vacancy": v["title"],
                         "company": self.s.companies[v["employer_id"]], "applicant": u["full_name"],
                         "status": a["status"], "app_date": "2026-10-29", "score": m["score"] if m else None})
        return rows
    def list_for_seeker(self, seeker_id):
        return self._rows([a for a in self.s.applications if a["seeker_id"] == seeker_id])
    def list_for_employer(self, employer_id):
        vids = {v["vacancy_id"] for v in self.s.vacancies if v["employer_id"] == employer_id}
        return self._rows([a for a in self.s.applications if a["vacancy_id"] in vids])
    def list_all(self):
        return self._rows(self.s.applications)


class FakeResumes:
    def __init__(self, s): self.s = s
    def get_by_seeker(self, seeker_id):
        return next((r for r in self.s.resumes if r["seeker_id"] == seeker_id), None)
    def save_match(self, resume_id, vacancy_id, score, model_version):
        self.s.matches.append({"resume_id": resume_id, "vacancy_id": vacancy_id, "score": score, "model": model_version})


class FakeCourses:
    def __init__(self, s): self.s = s
    def list_all(self): return list(self.s.courses)
    def is_enrolled(self, seeker_id, course_id): return (seeker_id, course_id) in self.s.enrollments
    def enroll(self, seeker_id, course_id): self.s.enrollments.append((seeker_id, course_id))


class FakeNotifications:
    def __init__(self, s): self.s = s
    def create(self, user_id, application_id, message):
        self.s.notifications.append({"notification_id": len(self.s.notifications) + 1, "user_id": user_id,
                                     "application_id": application_id, "message": message, "sent_at": "now"})
    def list_for_user(self, user_id):
        return [n for n in self.s.notifications if n["user_id"] == user_id]


def make_repos():
    s = FakeStore()
    return s, {
        "users": FakeUsers(s), "vacancies": FakeVacancies(s), "applications": FakeApplications(s),
        "resumes": FakeResumes(s), "courses": FakeCourses(s), "notifications": FakeNotifications(s),
    }
