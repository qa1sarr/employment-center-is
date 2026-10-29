from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from business.errors import AuthError, BusinessError


def create_blueprint(services: dict) -> Blueprint:
    """services: {'auth', 'vacancies', 'applications', 'courses', 'notifications', 'reports'}"""
    bp = Blueprint("web", __name__)

    def current_user():
        return session.get("user")

    @bp.app_context_processor
    def inject_user():
        return {"user": current_user()}

    def login_required(view):
        """Кірмеген пайдаланушыны /login-ге жібереді; бизнес-қатені хабар етіп көрсетеді."""
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user():
                return redirect(url_for("web.login"))
            try:
                return view(*args, **kwargs)
            except BusinessError as error:
                flash(str(error))
                return redirect(request.referrer or url_for("web.vacancies"))
        return wrapper

    @bp.route("/")
    def index():
        return redirect(url_for("web.vacancies"))

    @bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            try:
                session["user"] = services["auth"].login(
                    request.form.get("email"), request.form.get("password")
                )
                return redirect(url_for("web.vacancies"))
            except AuthError as error:
                flash(str(error))
        return render_template("login.html")

    @bp.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("web.login"))

    @bp.route("/vacancies")
    @login_required
    def vacancies():
        keyword = request.args.get("q", "")
        rows = services["vacancies"].search(keyword)
        return render_template("vacancies.html", vacancies=rows, q=keyword)

    @bp.route("/vacancies", methods=["POST"])
    @login_required
    def publish_vacancy():
        services["vacancies"].publish(
            current_user(),
            request.form.get("title"),
            request.form.get("requirements"),
            request.form.get("salary"),
        )
        flash("Вакансия жарияланды")
        return redirect(url_for("web.vacancies"))

    @bp.route("/vacancies/<int:vacancy_id>/close", methods=["POST"])
    @login_required
    def close_vacancy(vacancy_id):
        services["vacancies"].close(current_user(), vacancy_id)
        flash("Вакансия жабылды")
        return redirect(url_for("web.vacancies"))

    @bp.route("/vacancies/<int:vacancy_id>/apply", methods=["POST"])
    @login_required
    def apply(vacancy_id):
        result = services["applications"].apply(current_user(), vacancy_id)
        score = result["score"]
        flash("Өтінім қабылданды" + (f". Сәйкестік: {score}%" if score is not None else ""))
        return redirect(url_for("web.applications"))

    @bp.route("/applications")
    @login_required
    def applications():
        rows = services["applications"].list_for(current_user())
        return render_template("applications.html", applications=rows)

    @bp.route("/applications/<int:application_id>/status", methods=["POST"])
    @login_required
    def change_status(application_id):
        services["applications"].change_status(
            current_user(), application_id, request.form.get("status")
        )
        flash("Мәртебе өзгертілді")
        return redirect(url_for("web.applications"))

    @bp.route("/courses")
    @login_required
    def courses():
        return render_template("courses.html", courses=services["courses"].list_courses())

    @bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
    @login_required
    def enroll(course_id):
        services["courses"].enroll(current_user(), course_id)
        flash("Курсқа жазылдыңыз")
        return redirect(url_for("web.courses"))

    @bp.route("/notifications")
    @login_required
    def notifications():
        rows = services["notifications"].list_for(current_user())
        return render_template("notifications.html", notifications=rows)

    @bp.route("/reports")
    @login_required
    def reports():
        report = services["reports"].vacancy_report(current_user())
        return render_template("reports.html", report=report)

    return bp
