"""Көрсету деңгейі: HTTP маршруттары. Құқықтар қызметтерде де (business) тексеріледі."""
import hmac
import secrets
from functools import wraps
from urllib.parse import urlparse

from flask import (Blueprint, abort, flash, redirect, render_template, request,
                   session, url_for)

from business.errors import AuthError, BusinessError, NotFoundError, PermissionDenied
from business.permissions import require_role

ROLE_NAMES = {
    "job_seeker": "Жұмыс іздеуші", "employer": "Жұмыс беруші",
    "specialist": "Маман", "admin": "Әкімші",
}
APP_STATUS = {"submitted": "Берілді", "reviewed": "Қаралды",
              "accepted": "Қабылданды", "rejected": "Қабылданбады"}
VAC_STATUS = {"open": "Ашық", "closed": "Жабық"}

# (endpoint, белгі, иконка) — әр рөлге өз мәзірі
MENU = {
    "job_seeker": [
        ("web.dashboard", "Басты бет", "🏠"), ("web.vacancies", "Вакансиялар", "💼"),
        ("web.applications", "Менің өтінімдерім", "📨"), ("web.resume", "Менің түйіндемем", "📄"),
        ("web.courses", "Оқу курстары", "🎓"), ("web.notifications", "Хабарламалар", "🔔"),
        ("web.profile", "Профиль", "👤"),
    ],
    "employer": [
        ("web.dashboard", "Басты бет", "🏠"), ("web.vacancies", "Менің вакансияларым", "💼"),
        ("web.applications", "Түскен өтінімдер", "📨"), ("web.notifications", "Хабарламалар", "🔔"),
        ("web.profile", "Профиль", "👤"),
    ],
    "specialist": [
        ("web.dashboard", "Басты бет", "🏠"), ("web.seekers", "Жұмыс іздеушілер", "🧑‍💼"),
        ("web.vacancies", "Вакансиялар", "💼"), ("web.applications", "Өтінімдер", "📨"),
        ("web.courses", "Оқу курстары", "🎓"), ("web.reports", "Есептер", "📊"),
        ("web.notifications", "Хабарламалар", "🔔"), ("web.profile", "Профиль", "👤"),
    ],
    "admin": [
        ("web.dashboard", "Басты бет", "🏠"), ("web.users", "Пайдаланушылар", "👥"),
        ("web.vacancies", "Вакансиялар", "💼"), ("web.applications", "Өтінімдер", "📨"),
        ("web.seekers", "Жұмыс іздеушілер", "🧑‍💼"), ("web.courses", "Оқу курстары", "🎓"),
        ("web.reports", "Есептер", "📊"), ("web.notifications", "Хабарламалар", "🔔"),
        ("web.profile", "Профиль", "👤"),
    ],
}
DEMO_ACCOUNTS = [
    ("job_seeker", "aigerim@mail.kz"), ("employer", "bakyt@techno.kz"),
    ("specialist", "erlan@enbek.kz"), ("admin", "aidos@enbek.kz"),
]


def create_blueprint(services: dict, demo: bool = False, forced_mode: str = None) -> Blueprint:
    bp = Blueprint("web", __name__)

    # ---------- жалпы көмекшілер ----------
    def current_user():
        return session.get("user")

    def back(default="web.dashboard"):
        """Тек өз сайтымыздан келген referrer-ге қайтарады (open redirect болмауы үшін)."""
        ref = request.referrer
        if ref and urlparse(ref).netloc == request.host:
            return redirect(ref)
        return redirect(url_for(default))

    @bp.before_request
    def csrf_protect():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)
        if request.method == "POST":
            sent = request.form.get("csrf_token", "")
            if not hmac.compare_digest(sent, session["csrf"]):
                abort(400)

    @bp.app_context_processor
    def inject_globals():
        user = current_user()
        return {
            "user": user, "csrf_token": session.get("csrf", ""),
            "menu": MENU.get(user["role"], []) if user else [],
            "ROLE_NAMES": ROLE_NAMES, "APP_STATUS": APP_STATUS, "VAC_STATUS": VAC_STATUS,
            "demo": demo, "forced_mode": forced_mode, "login_mode": session.get("login_mode"),
        }

    @bp.app_template_filter("money")
    def money(value):
        if value is None:
            return "—"
        return "{:,.0f} ₸".format(float(value)).replace(",", " ")

    @bp.app_template_filter("fdate")
    def fdate(value):
        return str(value)[:10] if value is not None else "—"

    @bp.app_template_filter("fdt")
    def fdt(value):
        return str(value)[:16] if value is not None else "—"

    @bp.app_template_filter("initials")
    def initials(name):
        parts = (name or "?").split()
        return "".join(p[0] for p in parts[:2]).upper()

    @bp.app_errorhandler(400)
    def bad_request(error):
        return render_template("error.html", code=400,
                               message="Сұраныс жарамсыз немесе сессия мерзімі өтті. Бетті жаңартып, қайталаңыз."), 400

    @bp.app_errorhandler(404)
    def not_found(error):
        return render_template("error.html", code=404, message="Бет табылмады"), 404

    def login_required(view):
        """Кірмеген пайдаланушыны /login-ге жібереді; бизнес-қателерді өңдейді."""
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not current_user():
                return redirect(url_for("web.login"))
            try:
                return view(*args, **kwargs)
            except PermissionDenied as error:
                if request.method == "GET":
                    return render_template("error.html", code=403, message=str(error)), 403
                flash(str(error), "error")
                return back()
            except NotFoundError as error:
                if request.method == "GET":
                    return render_template("error.html", code=404, message=str(error)), 404
                flash(str(error), "error")
                return back()
            except BusinessError as error:
                flash(str(error), "error")
                return back()
        return wrapper

    def roles_required(*roles):
        def decorator(view):
            @login_required
            @wraps(view)
            def wrapper(*args, **kwargs):
                require_role(current_user(), *roles)
                return view(*args, **kwargs)
            return wrapper
        return decorator

    # ---------- кіру / шығу ----------
    @bp.route("/")
    def index():
        return redirect(url_for("web.dashboard" if current_user() else "web.login"))

    @bp.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email, password = request.form.get("email"), request.form.get("password")
            mode = forced_mode or (request.form.get("mode") if demo else "secure")
            try:
                if mode == "vulnerable":
                    user = services["auth"].login_vulnerable(email, password)
                else:
                    user = services["auth"].login(email, password)
            except AuthError as error:
                flash(str(error), "error")
            except Exception as error:  # осал режимде SQL синтаксис қатесі болуы мүмкін
                if mode != "vulnerable":
                    raise
                flash("SQL қатесі: %s" % error, "error")
            else:
                session.clear()
                session["user"] = user
                session["csrf"] = secrets.token_hex(16)
                session["login_mode"] = mode if (demo or forced_mode) else None
                return redirect(url_for("web.dashboard"))
        return render_template("login.html", demo_accounts=DEMO_ACCOUNTS)

    @bp.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("web.login"))

    # ---------- басты бет, профиль ----------
    @bp.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html", d=services["dashboard"].for_user(current_user()))

    @bp.route("/profile")
    @login_required
    def profile():
        return render_template("profile.html", p=services["auth"].profile(current_user()))

    @bp.route("/profile", methods=["POST"])
    @login_required
    def profile_update():
        session["user"] = services["auth"].update_contact(
            current_user(), request.form.get("full_name"), request.form.get("phone"))
        flash("Профиль жаңартылды", "ok")
        return redirect(url_for("web.profile"))

    @bp.route("/profile/password", methods=["POST"])
    @login_required
    def profile_password():
        services["auth"].change_password(
            current_user(), request.form.get("current"), request.form.get("new"),
            request.form.get("repeat"))
        flash("Құпиясөз өзгертілді", "ok")
        return redirect(url_for("web.profile"))

    # ---------- вакансиялар ----------
    @bp.route("/vacancies")
    @login_required
    def vacancies():
        q, status = request.args.get("q", ""), request.args.get("status", "")
        rows = services["vacancies"].list_for(current_user(), q, status)
        return render_template("vacancies.html", vacancies=rows, q=q, status=status)

    @bp.route("/vacancies/new")
    @roles_required("employer")
    def vacancy_new():
        return render_template("vacancy_form.html", v=None, form={})

    @bp.route("/vacancies", methods=["POST"])
    @roles_required("employer")
    def vacancy_create():
        f = request.form
        try:
            vacancy_id = services["vacancies"].publish(
                current_user(), f.get("title"), f.get("requirements"), f.get("salary"))
        except (PermissionDenied, NotFoundError):
            raise
        except BusinessError as error:
            flash(str(error), "error")
            return render_template("vacancy_form.html", v=None, form=f), 400
        flash("Вакансия жарияланды", "ok")
        return redirect(url_for("web.vacancy_detail", vacancy_id=vacancy_id))

    @bp.route("/vacancies/<int:vacancy_id>")
    @login_required
    def vacancy_detail(vacancy_id):
        return render_template("vacancy_detail.html",
                               d=services["vacancies"].detail(current_user(), vacancy_id))

    @bp.route("/vacancies/<int:vacancy_id>/edit")
    @roles_required("employer", "admin")
    def vacancy_edit(vacancy_id):
        v = services["vacancies"].get_for_edit(current_user(), vacancy_id)
        return render_template("vacancy_form.html", v=v, form=v)

    @bp.route("/vacancies/<int:vacancy_id>/edit", methods=["POST"])
    @roles_required("employer", "admin")
    def vacancy_update(vacancy_id):
        f = request.form
        try:
            services["vacancies"].update(
                current_user(), vacancy_id, f.get("title"), f.get("requirements"), f.get("salary"))
        except (PermissionDenied, NotFoundError):
            raise
        except BusinessError as error:
            flash(str(error), "error")
            v = services["vacancies"].get_for_edit(current_user(), vacancy_id)
            return render_template("vacancy_form.html", v=v, form=f), 400
        flash("Вакансия жаңартылды", "ok")
        return redirect(url_for("web.vacancy_detail", vacancy_id=vacancy_id))

    @bp.route("/vacancies/<int:vacancy_id>/close", methods=["POST"])
    @roles_required("employer", "admin")
    def vacancy_close(vacancy_id):
        services["vacancies"].close(current_user(), vacancy_id)
        flash("Вакансия жабылды", "ok")
        return back("web.vacancies")

    @bp.route("/vacancies/<int:vacancy_id>/reopen", methods=["POST"])
    @roles_required("employer", "admin")
    def vacancy_reopen(vacancy_id):
        services["vacancies"].reopen(current_user(), vacancy_id)
        flash("Вакансия қайта ашылды", "ok")
        return back("web.vacancies")

    @bp.route("/vacancies/<int:vacancy_id>/apply", methods=["POST"])
    @roles_required("job_seeker")
    def apply(vacancy_id):
        result = services["applications"].apply(current_user(), vacancy_id)
        score = result["score"]
        if score is not None:
            flash("Өтінім қабылданды. Сәйкестік: %s%%" % score, "ok")
        else:
            flash("Өтінім қабылданды. Түйіндемені толтырсаңыз, сәйкестік есептеледі", "ok")
        return redirect(url_for("web.applications"))

    # ---------- өтінімдер ----------
    @bp.route("/applications")
    @login_required
    def applications():
        return render_template("applications.html",
                               applications=services["applications"].list_for(current_user()))

    @bp.route("/applications/<int:application_id>/status", methods=["POST"])
    @roles_required("employer", "specialist", "admin")
    def application_status(application_id):
        services["applications"].change_status(
            current_user(), application_id, request.form.get("status"))
        flash("Мәртебе өзгертілді", "ok")
        return back("web.applications")

    # ---------- түйіндеме ----------
    @bp.route("/resume")
    @roles_required("job_seeker")
    def resume():
        return render_template("resume.html", r=services["resumes"].get(current_user()), form=None)

    @bp.route("/resume", methods=["POST"])
    @roles_required("job_seeker")
    def resume_save():
        f = request.form
        try:
            services["resumes"].save(current_user(), f.get("skills"), f.get("experience_years"),
                                     f.get("experience"), f.get("education"))
        except (PermissionDenied, NotFoundError):
            raise
        except BusinessError as error:
            flash(str(error), "error")
            return render_template("resume.html", r=services["resumes"].get(current_user()), form=f), 400
        flash("Түйіндеме сақталды", "ok")
        return redirect(url_for("web.resume"))

    # ---------- курстар ----------
    @bp.route("/courses")
    @login_required
    def courses():
        u = current_user()
        mine = services["courses"].my_courses(u) if u["role"] == "job_seeker" else []
        return render_template("courses.html", courses=services["courses"].list_for(u), mine=mine)

    @bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
    @roles_required("job_seeker")
    def course_enroll(course_id):
        services["courses"].enroll(current_user(), course_id)
        flash("Курсқа жазылдыңыз", "ok")
        return redirect(url_for("web.courses"))

    @bp.route("/courses", methods=["POST"])
    @roles_required("specialist", "admin")
    def course_create():
        f = request.form
        services["courses"].create(current_user(), f.get("name"), f.get("description"),
                                   f.get("duration_hours"))
        flash("Курс қосылды", "ok")
        return redirect(url_for("web.courses"))

    @bp.route("/courses/<int:course_id>/delete", methods=["POST"])
    @roles_required("admin")
    def course_delete(course_id):
        services["courses"].delete(current_user(), course_id)
        flash("Курс жойылды", "ok")
        return redirect(url_for("web.courses"))

    # ---------- жұмыс іздеушілер (маман, әкімші) ----------
    @bp.route("/seekers")
    @roles_required("specialist", "admin")
    def seekers():
        q = request.args.get("q", "")
        return render_template("seekers.html", seekers=services["seekers"].list(current_user(), q), q=q)

    @bp.route("/seekers/<int:seeker_id>")
    @roles_required("specialist", "admin")
    def seeker_detail(seeker_id):
        return render_template("seeker_detail.html",
                               d=services["seekers"].detail(current_user(), seeker_id))

    @bp.route("/seekers/<int:seeker_id>/assign", methods=["POST"])
    @roles_required("specialist", "admin")
    def seeker_assign(seeker_id):
        try:
            course_id = int(request.form.get("course_id", ""))
        except ValueError:
            raise BusinessError("Курсты таңдаңыз")
        services["seekers"].assign_course(current_user(), seeker_id, course_id)
        flash("Курс тағайындалды", "ok")
        return redirect(url_for("web.seeker_detail", seeker_id=seeker_id))

    # ---------- пайдаланушылар (әкімші) ----------
    @bp.route("/users")
    @roles_required("admin")
    def users():
        role = request.args.get("role", "")
        return render_template("users.html", users=services["users"].list(current_user(), role),
                               role=role)

    @bp.route("/users/new")
    @roles_required("admin")
    def user_new():
        return render_template("user_form.html", form={})

    @bp.route("/users", methods=["POST"])
    @roles_required("admin")
    def user_create():
        try:
            services["users"].create(current_user(), request.form)
        except (PermissionDenied, NotFoundError):
            raise
        except BusinessError as error:
            flash(str(error), "error")
            return render_template("user_form.html", form=request.form), 400
        flash("Пайдаланушы қосылды", "ok")
        return redirect(url_for("web.users"))

    @bp.route("/users/<int:user_id>/password", methods=["POST"])
    @roles_required("admin")
    def user_password(user_id):
        services["users"].reset_password(current_user(), user_id, request.form.get("new"))
        flash("Құпиясөз жаңартылды", "ok")
        return redirect(url_for("web.users"))

    # ---------- есептер, хабарламалар ----------
    @bp.route("/reports")
    @roles_required("specialist", "admin")
    def reports():
        return render_template("reports.html", report=services["reports"].vacancy_report(current_user()))

    @bp.route("/notifications")
    @login_required
    def notifications():
        return render_template("notifications.html",
                               notifications=services["notifications"].list_for(current_user()))

    return bp
