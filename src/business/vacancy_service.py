from .errors import BusinessError, PermissionDenied
from .permissions import require_role


class VacancyService:
    """Вакансиялар: іздеу, жариялау, жабу."""

    def __init__(self, vacancies):
        self.vacancies = vacancies

    def search(self, keyword=None):
        return self.vacancies.list_with_counts((keyword or "").strip() or None)

    def publish(self, user, title, requirements, salary) -> int:
        require_role(user, "employer")
        title = (title or "").strip()
        if not title:
            raise BusinessError("Вакансия атауын көрсетіңіз")
        try:
            salary = float(salary)
        except (TypeError, ValueError):
            raise BusinessError("Жалақы сан болуы керек")
        if salary < 0:
            raise BusinessError("Жалақы теріс болмауы керек")
        return self.vacancies.create(user["user_id"], title, (requirements or "").strip(), salary)

    def close(self, user, vacancy_id: int) -> None:
        require_role(user, "employer", "admin")
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise BusinessError("Вакансия табылмады")
        if user["role"] == "employer" and vacancy["employer_id"] != user["user_id"]:
            raise PermissionDenied("Бұл сіздің вакансияңыз емес")
        self.vacancies.close(vacancy_id)
