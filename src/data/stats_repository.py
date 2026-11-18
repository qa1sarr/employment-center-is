class StatsRepository:
    """Басты бет пен есептерге арналған жиынтық сандар."""

    def __init__(self, db):
        self.db = db

    def _as_dict(self, rows, key="k", value="n") -> dict:
        return {r[key]: int(r[value]) for r in rows}

    # --- жұмыс іздеуші ---
    def seeker_application_statuses(self, seeker_id: int) -> dict:
        return self._as_dict(self.db.query(
            "SELECT status AS k, COUNT(*) AS n FROM applications WHERE seeker_id = ? GROUP BY status",
            (seeker_id,)))

    def seeker_course_count(self, seeker_id: int) -> int:
        return int(self.db.query(
            "SELECT COUNT(*) AS n FROM enrollments WHERE seeker_id = ?", (seeker_id,))[0]["n"])

    def seeker_best_match(self, seeker_id: int):
        rows = self.db.query(
            "SELECT MAX(m.score) AS best FROM match_results m "
            "JOIN resumes r ON r.resume_id = m.resume_id WHERE r.seeker_id = ?",
            (seeker_id,))
        return rows[0]["best"] if rows else None

    # --- жұмыс беруші ---
    def employer_vacancy_statuses(self, employer_id: int) -> dict:
        return self._as_dict(self.db.query(
            "SELECT status AS k, COUNT(*) AS n FROM vacancies WHERE employer_id = ? GROUP BY status",
            (employer_id,)))

    def employer_application_statuses(self, employer_id: int) -> dict:
        return self._as_dict(self.db.query(
            "SELECT a.status AS k, COUNT(*) AS n FROM applications a "
            "JOIN vacancies v ON v.vacancy_id = a.vacancy_id "
            "WHERE v.employer_id = ? GROUP BY a.status",
            (employer_id,)))

    # --- маман / әкімші ---
    def users_by_role(self) -> dict:
        return self._as_dict(self.db.query("SELECT role AS k, COUNT(*) AS n FROM users GROUP BY role"))

    def vacancy_statuses(self) -> dict:
        return self._as_dict(self.db.query(
            "SELECT status AS k, COUNT(*) AS n FROM vacancies GROUP BY status"))

    def application_statuses(self) -> dict:
        return self._as_dict(self.db.query(
            "SELECT status AS k, COUNT(*) AS n FROM applications GROUP BY status"))

    def table_count(self, table: str) -> int:
        allowed = {"courses", "enrollments", "notifications", "match_results", "resumes"}
        if table not in allowed:
            raise ValueError("Рұқсат етілмеген кесте")
        return int(self.db.query("SELECT COUNT(*) AS n FROM " + table)[0]["n"])

    def industry_report(self) -> list:
        return self.db.query(
            "SELECT e.industry AS industry, COUNT(DISTINCT v.vacancy_id) AS vacancies, "
            "       COUNT(a.application_id) AS applications, "
            "       SUM(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) AS hired "
            "FROM employers e "
            "LEFT JOIN vacancies v ON v.employer_id = e.user_id "
            "LEFT JOIN applications a ON a.vacancy_id = v.vacancy_id "
            "GROUP BY e.industry ORDER BY applications DESC, e.industry"
        )
