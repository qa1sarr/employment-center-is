from datetime import date


class CourseRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self) -> list:
        return self.db.query(
            "SELECT c.course_id, c.name, c.description, c.duration_hours, "
            "       (SELECT COUNT(*) FROM enrollments en WHERE en.course_id = c.course_id) AS students "
            "FROM courses c ORDER BY c.course_id"
        )

    def get(self, course_id: int):
        rows = self.db.query(
            "SELECT course_id, name, description, duration_hours FROM courses WHERE course_id = ?",
            (course_id,),
        )
        return rows[0] if rows else None

    def is_enrolled(self, seeker_id: int, course_id: int) -> bool:
        rows = self.db.query(
            "SELECT 1 AS x FROM enrollments WHERE seeker_id = ? AND course_id = ?",
            (seeker_id, course_id),
        )
        return bool(rows)

    def enrolled_ids(self, seeker_id: int) -> set:
        rows = self.db.query("SELECT course_id FROM enrollments WHERE seeker_id = ?", (seeker_id,))
        return {r["course_id"] for r in rows}

    def enroll(self, seeker_id: int, course_id: int, assigned_by=None) -> None:
        self.db.execute(
            "INSERT INTO enrollments (seeker_id, course_id, assigned_by, enrolled_at) "
            "VALUES (?, ?, ?, ?)",
            (seeker_id, course_id, assigned_by, date.today().isoformat()),
        )

    def list_for_seeker(self, seeker_id: int) -> list:
        return self.db.query(
            "SELECT c.course_id, c.name, c.description, c.duration_hours, "
            "       en.enrolled_at, u.full_name AS assigned_by_name "
            "FROM enrollments en JOIN courses c ON c.course_id = en.course_id "
            "LEFT JOIN users u ON u.user_id = en.assigned_by "
            "WHERE en.seeker_id = ? ORDER BY en.enrolled_at DESC, c.course_id",
            (seeker_id,),
        )

    def create(self, name: str, description, duration_hours: int) -> int:
        return self.db.execute(
            "INSERT INTO courses (name, description, duration_hours) "
            "OUTPUT INSERTED.course_id VALUES (?, ?, ?)",
            (name, description, duration_hours),
            returns_id=True,
        )

    def delete(self, course_id: int) -> None:
        self.db.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
