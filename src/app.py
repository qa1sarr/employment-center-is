"""Қолданбаны іске қосу (composition root): үш деңгейді осы жерде жалғаймыз."""
from flask import Flask

import config
from business.application_service import ApplicationService
from business.auth_service import AuthService
from business.course_service import CourseService
from business.matching_service import MatchingService
from business.notification_service import NotificationService
from business.report_service import ReportService
from business.vacancy_service import VacancyService
from presentation.routes import create_blueprint


def build_services(repos: dict) -> dict:
    """Репозиторийлерден (деректер деңгейі) қызметтерді (логика деңгейі) құрады."""
    notifications = NotificationService(repos["notifications"])
    return {
        "auth": AuthService(repos["users"]),
        "vacancies": VacancyService(repos["vacancies"]),
        "applications": ApplicationService(
            repos["applications"], repos["vacancies"], repos["resumes"],
            MatchingService(), notifications,
        ),
        "courses": CourseService(repos["courses"]),
        "notifications": notifications,
        "reports": ReportService(repos["vacancies"]),
    }


def build_sql_repositories() -> dict:
    from data.application_repository import ApplicationRepository
    from data.course_repository import CourseRepository
    from data.database import Database
    from data.notification_repository import NotificationRepository
    from data.resume_repository import ResumeRepository
    from data.user_repository import UserRepository
    from data.vacancy_repository import VacancyRepository

    db = Database(config.connection_string())
    return {
        "users": UserRepository(db),
        "vacancies": VacancyRepository(db),
        "applications": ApplicationRepository(db),
        "resumes": ResumeRepository(db),
        "courses": CourseRepository(db),
        "notifications": NotificationRepository(db),
    }


def create_app(repos: dict = None) -> Flask:
    app = Flask(__name__, template_folder="presentation/templates")
    app.secret_key = config.SECRET_KEY
    services = build_services(repos or build_sql_repositories())
    app.register_blueprint(create_blueprint(services))
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
