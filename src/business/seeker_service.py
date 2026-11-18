from .errors import BusinessError, NotFoundError
from .permissions import require_role

STAFF = ("specialist", "admin")


class SeekerService:
    """Жұмыс іздеушілермен жұмыс (маман мен әкімші): тізім, карточка, курс тағайындау."""

    def __init__(self, seekers, courses, applications, resumes, notifier):
        self.seekers = seekers
        self.courses = courses
        self.applications = applications
        self.resumes = resumes
        self.notifier = notifier

    def list(self, user: dict, keyword=None) -> list:
        require_role(user, *STAFF)
        return self.seekers.list_seekers((keyword or "").strip() or None)

    def detail(self, user: dict, seeker_id: int) -> dict:
        require_role(user, *STAFF)
        seeker = self.seekers.get(seeker_id)
        if seeker is None:
            raise NotFoundError("Жұмыс іздеуші табылмады")
        taken = self.courses.enrolled_ids(seeker_id)
        return {
            "seeker": seeker,
            "resume": self.resumes.get_by_seeker(seeker_id) or {},
            "applications": self.applications.list_for_seeker(seeker_id),
            "courses": self.courses.list_for_seeker(seeker_id),
            "available_courses": [c for c in self.courses.list_all() if c["course_id"] not in taken],
        }

    def assign_course(self, user: dict, seeker_id: int, course_id: int) -> None:
        require_role(user, *STAFF)
        if self.seekers.get(seeker_id) is None:
            raise NotFoundError("Жұмыс іздеуші табылмады")
        course = self.courses.get(course_id)
        if course is None:
            raise NotFoundError("Курс табылмады")
        if self.courses.is_enrolled(seeker_id, course_id):
            raise BusinessError("Бұл курс іздеушіге бұрын тағайындалған")
        # assigned_by — specialists кестесіне сілтеме; әкімші тағайындаса, бос қалады
        assigned_by = user["user_id"] if user["role"] == "specialist" else None
        self.courses.enroll(seeker_id, course_id, assigned_by)
        self.notifier.notify(seeker_id, None, f"Сізге «{course['name']}» курсы тағайындалды")
