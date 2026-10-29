class VacancyRepository:
    def __init__(self, db):
        self.db = db

    def list_with_counts(self, keyword=None):
        """Барлық вакансия + тіркелгендер саны + жұмысқа тұрғандар саны."""
        sql = (
            "SELECT v.vacancy_id, v.title, e.company_name AS company, v.salary, v.status, "
            "       COUNT(a.application_id) AS applicants, "
            "       SUM(CASE WHEN a.status = N'accepted' THEN 1 ELSE 0 END) AS hired "
            "FROM vacancies v "
            "JOIN employers e ON e.user_id = v.employer_id "
            "LEFT JOIN applications a ON a.vacancy_id = v.vacancy_id "
        )
        params = ()
        if keyword:
            sql += "WHERE v.title LIKE ? "
            params = (f"%{keyword}%",)
        sql += (
            "GROUP BY v.vacancy_id, v.title, e.company_name, v.salary, v.status "
            "ORDER BY applicants DESC, v.title"
        )
        return self.db.query(sql, params)

    def get(self, vacancy_id: int):
        rows = self.db.query(
            "SELECT vacancy_id, employer_id, title, requirements, salary, status "
            "FROM vacancies WHERE vacancy_id = ?",
            (vacancy_id,),
        )
        return rows[0] if rows else None

    def create(self, employer_id: int, title: str, requirements: str, salary: float) -> int:
        return self.db.execute(
            "INSERT INTO vacancies (employer_id, title, requirements, salary) "
            "OUTPUT INSERTED.vacancy_id VALUES (?, ?, ?, ?)",
            (employer_id, title, requirements, salary),
            returns_id=True,
        )

    def close(self, vacancy_id: int) -> None:
        self.db.execute(
            "UPDATE vacancies SET status = N'closed' WHERE vacancy_id = ?",
            (vacancy_id,),
        )
