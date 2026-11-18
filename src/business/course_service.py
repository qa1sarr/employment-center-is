from .errors import BusinessError, NotFoundError
from .permissions import require_role


class CourseService:
    """Оқыту курстары: тізім, жазылу, құру, жою."""

    def __init__(self, courses):
        self.courses = courses

    def list_for(self, user: dict) -> list:
        courses = self.courses.list_all()
        enrolled = self.courses.enrolled_ids(user["user_id"]) if user["role"] == "job_seeker" else set()
        return [{**c, "enrolled": c["course_id"] in enrolled} for c in courses]

    def my_courses(self, user: dict) -> list:
        require_role(user, "job_seeker")
        return self.courses.list_for_seeker(user["user_id"])

    def enroll(self, user: dict, course_id: int) -> None:
        require_role(user, "job_seeker")
        if self.courses.get(course_id) is None:
            raise NotFoundError("Курс табылмады")
        if self.courses.is_enrolled(user["user_id"], course_id):
            raise BusinessError("Сіз бұл курсқа жазылып қойғансыз")
        self.courses.enroll(user["user_id"], course_id)

    def create(self, user: dict, name, description, duration_hours) -> int:
        require_role(user, "specialist", "admin")
        name = (name or "").strip()
        if not name:
            raise BusinessError("Курс атауын көрсетіңіз")
        try:
            hours = int(str(duration_hours).strip())
        except ValueError:
            raise BusinessError("Сағат саны бүтін сан болуы керек")
        if hours <= 0:
            raise BusinessError("Сағат саны оң болуы керек")
        return self.courses.create(name, (description or "").strip() or None, hours)

    def delete(self, user: dict, course_id: int) -> None:
        require_role(user, "admin")
        if self.courses.get(course_id) is None:
            raise NotFoundError("Курс табылмады")
        self.courses.delete(course_id)
