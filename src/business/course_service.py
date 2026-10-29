from .errors import BusinessError
from .permissions import require_role


class CourseService:
    """Оқыту курстары: тізім және курсқа жазылу."""

    def __init__(self, courses):
        self.courses = courses

    def list_courses(self):
        return self.courses.list_all()

    def enroll(self, user: dict, course_id: int) -> None:
        require_role(user, "job_seeker")
        if not any(c["course_id"] == course_id for c in self.courses.list_all()):
            raise BusinessError("Курс табылмады")
        if self.courses.is_enrolled(user["user_id"], course_id):
            raise BusinessError("Сіз бұл курсқа жазылып қойғансыз")
        self.courses.enroll(user["user_id"], course_id)
