from .errors import BusinessError, PermissionDenied
from .permissions import require_role

STATUSES = ("submitted", "reviewed", "accepted", "rejected")
STATUS_TEXT = {
    "submitted": "берілді",
    "reviewed": "қаралды",
    "accepted": "қабылданды",
    "rejected": "қабылданбады",
}


class ApplicationService:
    """Өтінімдерді өңдеу: тіркеу, сәйкестік баллын есептеу, мәртебені өзгерту."""

    def __init__(self, applications, vacancies, resumes, matching, notifier):
        self.applications = applications
        self.vacancies = vacancies
        self.resumes = resumes
        self.matching = matching
        self.notifier = notifier

    def apply(self, user: dict, vacancy_id: int) -> dict:
        # 1. Рөлді тексеру
        require_role(user, "job_seeker")
        # 2. Вакансия бар және ашық па?
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise BusinessError("Вакансия табылмады")
        if vacancy["status"] != "open":
            raise BusinessError("Вакансия жабық")
        # 3. Қайталанбайтынын тексеру
        if self.applications.exists(user["user_id"], vacancy_id):
            raise BusinessError("Сіз бұл вакансияға өтінім беріп қойғансыз")
        # 4. Өтінімді сақтау
        application_id = self.applications.create(user["user_id"], vacancy_id)
        # 5. Сәйкестік баллын есептеп, сақтау
        score = None
        resume = self.resumes.get_by_seeker(user["user_id"])
        if resume:
            score = self.matching.score(resume["skills"], vacancy["requirements"])
            self.resumes.save_match(
                resume["resume_id"], vacancy_id, score, self.matching.MODEL_VERSION
            )
        # 6. Жұмыс берушіге хабарлама жіберу
        self.notifier.notify(
            vacancy["employer_id"],
            application_id,
            f"{vacancy['title']} вакансиясына жаңа өтінім түсті",
        )
        return {"application_id": application_id, "score": score}

    def change_status(self, user: dict, application_id: int, new_status: str) -> None:
        require_role(user, "employer", "specialist", "admin")
        if new_status not in STATUSES:
            raise BusinessError("Белгісіз мәртебе")
        application = self.applications.get(application_id)
        if application is None:
            raise BusinessError("Өтінім табылмады")
        if user["role"] == "employer" and application["employer_id"] != user["user_id"]:
            raise PermissionDenied("Бұл сіздің вакансияңыздың өтініміне жатпайды")
        self.applications.update_status(application_id, new_status)
        self.notifier.notify(
            application["seeker_id"],
            application_id,
            f"«{application['vacancy_title']}» өтінімінің мәртебесі: {STATUS_TEXT[new_status]}",
        )

    def list_for(self, user: dict):
        if user["role"] == "job_seeker":
            return self.applications.list_for_seeker(user["user_id"])
        if user["role"] == "employer":
            return self.applications.list_for_employer(user["user_id"])
        return self.applications.list_all()
