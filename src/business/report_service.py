from .permissions import require_role


class ReportService:
    """Есеп беру модулі: вакансиялар мен өтінімдер бойынша жиынтық."""

    def __init__(self, vacancies):
        self.vacancies = vacancies

    def vacancy_report(self, user: dict) -> dict:
        require_role(user, "specialist", "admin")
        rows = self.vacancies.list_with_counts(None)
        return {
            "rows": rows,
            "total_vacancies": len(rows),
            "total_applicants": sum(int(r["applicants"]) for r in rows),
            "total_hired": sum(int(r["hired"]) for r in rows),
        }
