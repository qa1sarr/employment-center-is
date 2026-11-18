APP_STATUSES = ("submitted", "reviewed", "accepted", "rejected")


def _full(counts: dict, keys) -> dict:
    return {k: int(counts.get(k, 0)) for k in keys}


class DashboardService:
    """Басты бет: әр рөлге өз көрсеткіштері (өз деректері ғана)."""

    def __init__(self, stats, applications, notifications):
        self.stats = stats
        self.applications = applications
        self.notifications = notifications

    def for_user(self, user: dict) -> dict:
        role = user["role"]
        build = {
            "job_seeker": self._seeker,
            "employer": self._employer,
            "specialist": self._staff,
            "admin": self._staff,
        }[role]
        data = build(user)
        data["notifications"] = self.notifications.list_for_user(user["user_id"])[:5]
        data["role"] = role
        return data

    def _seeker(self, user):
        uid = user["user_id"]
        apps = _full(self.stats.seeker_application_statuses(uid), APP_STATUSES)
        best = self.stats.seeker_best_match(uid)
        return {
            "tiles": [
                {"label": "Берілген өтінімдер", "value": sum(apps.values())},
                {"label": "Қабылданды", "value": apps["accepted"]},
                {"label": "Оқу курстары", "value": self.stats.seeker_course_count(uid)},
                {"label": "Ең жоғары сәйкестік", "value": "%s%%" % best if best is not None else "—"},
            ],
            "breakdown_title": "Өтінімдер мәртебесі бойынша",
            "breakdown": apps,
            "recent": self.applications.list_for_seeker(uid)[:5],
        }

    def _employer(self, user):
        uid = user["user_id"]
        vac = _full(self.stats.employer_vacancy_statuses(uid), ("open", "closed"))
        apps = _full(self.stats.employer_application_statuses(uid), APP_STATUSES)
        return {
            "tiles": [
                {"label": "Ашық вакансиялар", "value": vac["open"]},
                {"label": "Жабық вакансиялар", "value": vac["closed"]},
                {"label": "Түскен өтінімдер", "value": sum(apps.values())},
                {"label": "Жұмысқа алынды", "value": apps["accepted"]},
            ],
            "breakdown_title": "Өтінімдер мәртебесі бойынша",
            "breakdown": apps,
            "recent": self.applications.list_for_employer(uid)[:5],
        }

    def _staff(self, user):
        roles = self.stats.users_by_role()
        vac = _full(self.stats.vacancy_statuses(), ("open", "closed"))
        apps = _full(self.stats.application_statuses(), APP_STATUSES)
        tiles = [
            {"label": "Жұмыс іздеушілер", "value": int(roles.get("job_seeker", 0))},
            {"label": "Ашық вакансиялар", "value": vac["open"]},
            {"label": "Барлық өтінімдер", "value": sum(apps.values())},
            {"label": "Жұмысқа алынды", "value": apps["accepted"]},
        ]
        if user["role"] == "admin":
            tiles = [
                {"label": "Пайдаланушылар", "value": sum(int(v) for v in roles.values())},
                {"label": "Вакансиялар", "value": sum(vac.values())},
                {"label": "Өтінімдер", "value": sum(apps.values())},
                {"label": "Оқу курстары", "value": self.stats.table_count("courses")},
            ]
        return {
            "tiles": tiles,
            "breakdown_title": "Өтінімдер мәртебесі бойынша",
            "breakdown": apps,
            "roles": {k: int(v) for k, v in roles.items()},
            "recent": self.applications.list_all()[:5],
        }
