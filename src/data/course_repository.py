class CourseRepository:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self.db.query(
            "SELECT course_id, name, description, duration_hours "
            "FROM courses ORDER BY course_id"
        )

    def is_enrolled(self, seeker_id: int, course_id: int) -> bool:
        rows = self.db.query(
            "SELECT 1 AS x FROM enrollments WHERE seeker_id = ? AND course_id = ?",
            (seeker_id, course_id),
        )
        return bool(rows)

    def enroll(self, seeker_id: int, course_id: int) -> None:
        self.db.execute(
            "INSERT INTO enrollments (seeker_id, course_id) VALUES (?, ?)",
            (seeker_id, course_id),
        )
