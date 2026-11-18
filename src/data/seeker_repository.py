_SELECT = (
    "SELECT u.user_id, u.full_name, u.email, u.phone, js.education, js.skills, "
    "       r.resume_id, r.experience_years, "
    "       (SELECT COUNT(*) FROM applications a WHERE a.seeker_id = u.user_id) AS applications, "
    "       (SELECT COUNT(*) FROM applications a WHERE a.seeker_id = u.user_id "
    "          AND a.status = 'accepted') AS hired, "
    "       (SELECT COUNT(*) FROM enrollments en WHERE en.seeker_id = u.user_id) AS courses "
    "FROM users u JOIN job_seekers js ON js.user_id = u.user_id "
    "LEFT JOIN resumes r ON r.seeker_id = u.user_id "
)


class SeekerRepository:
    """Жұмыс іздеушілер тізімі (маман мен әкімші үшін)."""

    def __init__(self, db):
        self.db = db

    def list_seekers(self, keyword=None) -> list:
        if keyword:
            pattern = "%" + keyword + "%"
            return self.db.query(
                _SELECT + "WHERE u.full_name LIKE ? OR js.skills LIKE ? ORDER BY u.full_name",
                (pattern, pattern),
            )
        return self.db.query(_SELECT + "ORDER BY u.full_name")

    def get(self, seeker_id: int):
        rows = self.db.query(_SELECT + "WHERE u.user_id = ?", (seeker_id,))
        return rows[0] if rows else None
