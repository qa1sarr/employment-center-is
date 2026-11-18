"""Қолданбаны іске қосу (composition root): үш деңгейді осы жерде жалғаймыз."""
from flask import Flask

import config
from business.application_service import ApplicationService
from business.auth_service import AuthService
from business.course_service import CourseService
from business.dashboard_service import DashboardService
from business.matching_service import MatchingService
from business.notification_service import NotificationService
from business.report_service import ReportService
from business.resume_service import ResumeService
from business.seeker_service import SeekerService
from business.user_service import UserService
from business.vacancy_service import VacancyService
from presentation.routes import create_blueprint


def build_services(repos: dict, demo: bool = False) -> dict:
    """Репозиторийлерден (деректер деңгейі) қызметтерді (логика деңгейі) құрады."""
    notifications = NotificationService(repos["notifications"])
    matching = MatchingService()
    return {
        "auth": AuthService(repos["users"], demo=demo),
        "dashboard": DashboardService(repos["stats"], repos["applications"], repos["notifications"]),
        "vacancies": VacancyService(repos["vacancies"], repos["resumes"], matching, repos["applications"]),
        "applications": ApplicationService(
            repos["applications"], repos["vacancies"], repos["resumes"], matching, notifications,
        ),
        "resumes": ResumeService(repos["resumes"]),
        "courses": CourseService(repos["courses"]),
        "seekers": SeekerService(
            repos["seekers"], repos["courses"], repos["applications"], repos["resumes"], notifications,
        ),
        "users": UserService(repos["users"]),
        "notifications": notifications,
        "reports": ReportService(repos["vacancies"], repos["stats"]),
    }


def build_sql_repositories(db=None) -> dict:
    from data.application_repository import ApplicationRepository
    from data.course_repository import CourseRepository
    from data.database import Database
    from data.notification_repository import NotificationRepository
    from data.resume_repository import ResumeRepository
    from data.seeker_repository import SeekerRepository
    from data.stats_repository import StatsRepository
    from data.user_repository import UserRepository
    from data.vacancy_repository import VacancyRepository

    db = db or Database(config.connection_string())
    return {
        "users": UserRepository(db),
        "vacancies": VacancyRepository(db),
        "applications": ApplicationRepository(db),
        "resumes": ResumeRepository(db),
        "courses": CourseRepository(db),
        "notifications": NotificationRepository(db),
        "seekers": SeekerRepository(db),
        "stats": StatsRepository(db),
    }


def create_app(repos: dict = None, demo: bool = None, forced_mode: str = None) -> Flask:
    demo = config.LAB11_DEMO if demo is None else demo
    app = Flask(
        __name__,
        template_folder="presentation/templates",
        static_folder="presentation/static",
    )
    app.secret_key = config.SECRET_KEY
    app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
    services = build_services(repos or build_sql_repositories(), demo=demo)
    app.register_blueprint(create_blueprint(services, demo=demo, forced_mode=forced_mode))
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
