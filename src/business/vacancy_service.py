from .errors import BusinessError, NotFoundError, PermissionDenied
from .permissions import require_role

STATUSES = ("open", "closed")


def _clean(title, requirements, salary):
    title = (title or "").strip()
    if not title:
        raise BusinessError("Вакансия атауын көрсетіңіз")
    if len(title) > 150:
        raise BusinessError("Атауы 150 таңбадан аспауы керек")
    try:
        salary = float(str(salary).replace(" ", "").replace(",", "."))
    except (TypeError, ValueError):
        raise BusinessError("Жалақы сан болуы керек")
    if salary < 0:
        raise BusinessError("Жалақы теріс болмауы керек")
    return title, (requirements or "").strip(), salary


class VacancyService:
    """Вакансиялар: іздеу, көру, жариялау, өзгерту, жабу/қайта ашу."""

    def __init__(self, vacancies, resumes=None, matching=None, applications=None):
        self.vacancies = vacancies
        self.resumes = resumes
        self.matching = matching
        self.applications = applications

    def _score(self, resume, vacancy):
        if resume and resume.get("resume_id") is not None and self.matching:
            return self.matching.score(resume["skills"], vacancy["requirements"])
        return None

    def list_for(self, user: dict, keyword=None, status=None) -> list:
        """Рөлге қарай: іздеуші — тек ашық; жұмыс беруші — өз вакансиялары; қалғаны — барлығы."""
        keyword = (keyword or "").strip() or None
        status = status if status in STATUSES else None
        role = user["role"]
        if role == "job_seeker":
            rows = self.vacancies.list_with_counts(keyword, status="open")
            resume = self.resumes.get_by_seeker(user["user_id"]) if self.resumes else None
            applied = self.applications.applied_vacancy_ids(user["user_id"]) if self.applications else set()
            return [{**v, "score": self._score(resume, v), "applied": v["vacancy_id"] in applied}
                    for v in rows]
        if role == "employer":
            return self.vacancies.list_with_counts(keyword, employer_id=user["user_id"], status=status)
        return self.vacancies.list_with_counts(keyword, status=status)

    def _own_or_staff(self, user: dict, vacancy: dict) -> None:
        if user["role"] == "employer" and vacancy["employer_id"] != user["user_id"]:
            raise PermissionDenied("Бұл сіздің вакансияңыз емес")

    def detail(self, user: dict, vacancy_id: int) -> dict:
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise NotFoundError("Вакансия табылмады")
        role = user["role"]
        result = {"vacancy": vacancy, "score": None, "applied": False,
                  "applicants": None, "resume_missing": False, "can_manage": False}
        if role == "job_seeker":
            resume = self.resumes.get_by_seeker(user["user_id"]) if self.resumes else None
            result["score"] = self._score(resume, vacancy)
            result["resume_missing"] = not resume or resume.get("resume_id") is None
            result["applied"] = self.applications.exists(user["user_id"], vacancy_id)
        else:
            self._own_or_staff(user, vacancy)
            result["applicants"] = self.applications.list_for_vacancy(vacancy_id)
            result["can_manage"] = role in ("employer", "admin")
        return result

    def get_for_edit(self, user: dict, vacancy_id: int) -> dict:
        require_role(user, "employer", "admin")
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise NotFoundError("Вакансия табылмады")
        self._own_or_staff(user, vacancy)
        return vacancy

    def publish(self, user: dict, title, requirements, salary) -> int:
        require_role(user, "employer")
        title, requirements, salary = _clean(title, requirements, salary)
        return self.vacancies.create(user["user_id"], title, requirements, salary)

    def update(self, user: dict, vacancy_id: int, title, requirements, salary) -> None:
        self.get_for_edit(user, vacancy_id)
        title, requirements, salary = _clean(title, requirements, salary)
        self.vacancies.update(vacancy_id, title, requirements, salary)

    def set_status(self, user: dict, vacancy_id: int, status: str) -> None:
        if status not in STATUSES:
            raise BusinessError("Белгісіз күй")
        self.get_for_edit(user, vacancy_id)
        self.vacancies.set_status(vacancy_id, status)

    def close(self, user: dict, vacancy_id: int) -> None:
        self.set_status(user, vacancy_id, "closed")

    def reopen(self, user: dict, vacancy_id: int) -> None:
        self.set_status(user, vacancy_id, "open")
