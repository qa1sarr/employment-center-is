_SELECT = (
    "SELECT v.vacancy_id, v.employer_id, v.title, v.requirements, v.salary, v.status, "
    "       v.published_at, e.company_name AS company, e.industry, "
    "       (SELECT COUNT(*) FROM applications a WHERE a.vacancy_id = v.vacancy_id) AS applicants, "
    "       (SELECT COUNT(*) FROM applications a WHERE a.vacancy_id = v.vacancy_id "
    "          AND a.status = 'accepted') AS hired "
    "FROM vacancies v JOIN employers e ON e.user_id = v.employer_id "
)


class VacancyRepository:
    def __init__(self, db):
        self.db = db

    def list_with_counts(self, keyword=None, employer_id=None, status=None) -> list:
        """Вакансиялар + тіркелгендер саны + жұмысқа тұрғандар саны (сүзгілермен)."""
        where, params = [], []
        if keyword:
            where.append("(v.title LIKE ? OR v.requirements LIKE ?)")
            params += ["%" + keyword + "%", "%" + keyword + "%"]
        if employer_id is not None:
            where.append("v.employer_id = ?")
            params.append(employer_id)
        if status:
            where.append("v.status = ?")
            params.append(status)
        sql = _SELECT + ("WHERE " + " AND ".join(where) + " " if where else "")
        sql += "ORDER BY v.published_at DESC, v.vacancy_id DESC"
        return self.db.query(sql, tuple(params))

    def get(self, vacancy_id: int):
        rows = self.db.query(_SELECT + "WHERE v.vacancy_id = ?", (vacancy_id,))
        return rows[0] if rows else None

    def create(self, employer_id: int, title: str, requirements: str, salary: float) -> int:
        return self.db.execute(
            "INSERT INTO vacancies (employer_id, title, requirements, salary) "
            "OUTPUT INSERTED.vacancy_id VALUES (?, ?, ?, ?)",
            (employer_id, title, requirements, salary),
            returns_id=True,
        )

    def update(self, vacancy_id: int, title: str, requirements: str, salary: float) -> None:
        self.db.execute(
            "UPDATE vacancies SET title = ?, requirements = ?, salary = ? WHERE vacancy_id = ?",
            (title, requirements, salary, vacancy_id),
        )

    def set_status(self, vacancy_id: int, status: str) -> None:
        self.db.execute(
            "UPDATE vacancies SET status = ? WHERE vacancy_id = ?",
            (status, vacancy_id),
        )
