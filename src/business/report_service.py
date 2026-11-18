from .permissions import require_role


class ReportService:
    """Есеп беру модулі: вакансиялар, өтінімдер және салалар бойынша жиынтық."""

    def __init__(self, vacancies, stats):
        self.vacancies = vacancies
        self.stats = stats

    def vacancy_report(self, user: dict) -> dict:
        require_role(user, "specialist", "admin")
        rows = self.vacancies.list_with_counts(None)
        industries = [
            {**r, "hired": int(r["hired"] or 0), "applications": int(r["applications"] or 0)}
            for r in self.stats.industry_report()
        ]
        return {
            "rows": rows,
            "industries": industries,
            "total_vacancies": len(rows),
            "total_applicants": sum(int(r["applicants"]) for r in rows),
            "total_hired": sum(int(r["hired"]) for r in rows),
        }
