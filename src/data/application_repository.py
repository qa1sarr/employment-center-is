_LIST_SQL = (
    "SELECT a.application_id, v.title AS vacancy, e.company_name AS company, "
    "       u.full_name AS applicant, a.status, a.app_date, m.score "
    "FROM applications a "
    "JOIN vacancies v ON v.vacancy_id = a.vacancy_id "
    "JOIN employers e ON e.user_id = v.employer_id "
    "JOIN users u ON u.user_id = a.seeker_id "
    "LEFT JOIN resumes r ON r.seeker_id = a.seeker_id "
    "LEFT JOIN match_results m ON m.resume_id = r.resume_id AND m.vacancy_id = v.vacancy_id "
)
_ORDER = "ORDER BY a.app_date DESC, a.application_id DESC"


class ApplicationRepository:
    def __init__(self, db):
        self.db = db

    def exists(self, seeker_id: int, vacancy_id: int) -> bool:
        rows = self.db.query(
            "SELECT 1 AS x FROM applications WHERE seeker_id = ? AND vacancy_id = ?",
            (seeker_id, vacancy_id),
        )
        return bool(rows)

    def create(self, seeker_id: int, vacancy_id: int) -> int:
        return self.db.execute(
            "INSERT INTO applications (seeker_id, vacancy_id) "
            "OUTPUT INSERTED.application_id VALUES (?, ?)",
            (seeker_id, vacancy_id),
            returns_id=True,
        )

    def get(self, application_id: int):
        rows = self.db.query(
            "SELECT a.application_id, a.seeker_id, a.vacancy_id, a.status, "
            "       v.title AS vacancy_title, v.employer_id "
            "FROM applications a JOIN vacancies v ON v.vacancy_id = a.vacancy_id "
            "WHERE a.application_id = ?",
            (application_id,),
        )
        return rows[0] if rows else None

    def update_status(self, application_id: int, status: str) -> None:
        self.db.execute(
            "UPDATE applications SET status = ? WHERE application_id = ?",
            (status, application_id),
        )

    def list_for_seeker(self, seeker_id: int):
        return self.db.query(_LIST_SQL + "WHERE a.seeker_id = ? " + _ORDER, (seeker_id,))

    def list_for_employer(self, employer_id: int):
        return self.db.query(_LIST_SQL + "WHERE v.employer_id = ? " + _ORDER, (employer_id,))

    def list_all(self):
        return self.db.query(_LIST_SQL + _ORDER)
