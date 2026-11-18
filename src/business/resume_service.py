from .errors import BusinessError
from .permissions import require_role


class ResumeService:
    """Түйіндеме: жұмыс іздеуші тек өз түйіндемесін көреді және өзгертеді."""

    def __init__(self, resumes):
        self.resumes = resumes

    def get(self, user: dict) -> dict:
        require_role(user, "job_seeker")
        return self.resumes.get_by_seeker(user["user_id"]) or {}

    def save(self, user: dict, skills, experience_years, experience, education) -> None:
        require_role(user, "job_seeker")
        skills = (skills or "").strip()
        if not skills:
            raise BusinessError("Дағдыларыңызды көрсетіңіз (үтірмен бөліп)")
        try:
            years = int(str(experience_years).strip() or 0)
        except ValueError:
            raise BusinessError("Тәжірибе жылы бүтін сан болуы керек")
        if years < 0 or years > 60:
            raise BusinessError("Тәжірибе жылы 0–60 аралығында болуы керек")
        self.resumes.save(
            user["user_id"], skills, years,
            (experience or "").strip() or None, (education or "").strip() or None,
        )
