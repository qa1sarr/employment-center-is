"""Білім қоры: жүйе ережелері (қолмен жазылған) + өз базамыздағы деректер (вакансиялар, курстар)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Жүйенің нақты ережелері (қолданбадағы шынайы мінез-құлыққа сәйкес)
STATIC_DOCS = [
    "Жұмыспен қамту орталығының ақпараттық жүйесінде төрт рөл бар: жұмыс іздеуші, жұмыс беруші, маман және әкімші.",
    "Жұмыс іздеуші жүйеге email және құпиясөзбен кіреді. Құпиясөз кемінде 6 таңбадан тұруы керек.",
    "Жұмыс іздеуші тек ашық вакансияларды көреді және «Өтінім беру» батырмасымен өтінім береді.",
    "Жабық вакансияға өтінім беруге болмайды.",
    "Бір вакансияға бір жұмыс іздеуші тек бір рет өтінім бере алады.",
    "Өтінім мәртебелері: Берілді, Қаралды, Қабылданды, Қабылданбады.",
    "Өтінімнің мәртебесі өзгергенде жұмыс іздеушіге хабарлама жіберіледі.",
    "Түйіндемеде дағдылар, жұмыс өтілі, білімі және тәжірибесі көрсетіледі.",
    "Сәйкестік балы түйіндемедегі дағдылардың вакансия талаптарын қанша пайыз қамтитынын көрсетеді.",
    "Түйіндеме толтырылмаса, сәйкестік балы есептелмейді, бірақ өтінім беруге болады.",
    "Жұмыс беруші вакансия жариялайды, өзгертеді, жабады және қайта ашады.",
    "Жұмыс беруші тек өз вакансияларына түскен өтінімдерді көреді және олардың мәртебесін өзгертеді.",
    "Жұмыс іздеуші оқу курсына өзі жазыла алады, сондай-ақ маман оған курс тағайындай алады.",
    "Маман жұмыс іздеушілердің тізімін көреді, курс тағайындайды және есептерді қарайды.",
    "Әкімші пайдаланушыларды қосады, құпиясөзді жаңартады, курстарды жояды.",
]


_STATUS = {"submitted": "Берілді", "reviewed": "Қаралды", "accepted": "Қабылданды", "rejected": "Қабылданбады"}
_ROLE = {"job_seeker": "жұмыс іздеуші", "employer": "жұмыс беруші", "specialist": "маман", "admin": "әкімші"}
_REAL = "u.email not like '%@ml.demo'"  # Lab 12-нің демо деректері кірмейді


def _join(items, empty="жоқ"):
    return "; ".join(items) if items else empty


def db_documents(db) -> list:
    """Базаның барлық кестесіндегі деректерді мәтіндік құжатқа айналдырады.
    Email, телефон, құпиясөз хэші сияқты жеке деректер кірмейді."""
    docs = []
    q = db.query

    # --- вакансиялар (өтініш саны мен жұмыс берушімен бірге) ---
    apps_by_vac = {}
    for a in q("select vacancy_id, count(*) as n from applications group by vacancy_id"):
        apps_by_vac[a["vacancy_id"]] = int(a["n"])
    vacancies = q(
        "select v.vacancy_id, v.title, v.requirements, v.salary, v.status, v.published_at, "
        "e.company_name, u.full_name from vacancies v "
        "join employers e on e.user_id = v.employer_id join users u on u.user_id = e.user_id "
        "where v.title not like 'Демо%' and " + _REAL + " order by v.vacancy_id")
    vac_title = {}
    for v in vacancies:
        vac_title[v["vacancy_id"]] = v["title"]
        state = "ашық" if v["status"] == "open" else "жабық"
        docs.append(
            "%s вакансиясы: компания «%s», талаптар: %s, жалақы %d теңге, күйі: %s. "
            "Жұмыс беруші: %s. Жарияланған күні: %s. Түскен өтініш саны: %d."
            % (v["title"], v["company_name"], v["requirements"] or "көрсетілмеген",
               int(float(v["salary"])), state, v["full_name"], v["published_at"],
               apps_by_vac.get(v["vacancy_id"], 0)))

    # --- компаниялар ---
    by_company = {}
    for v in vacancies:
        by_company.setdefault(v["company_name"], []).append(v)
    for e in q("select e.company_name, e.industry, u.full_name from employers e "
               "join users u on u.user_id = e.user_id where " + _REAL + " order by e.user_id"):
        vs = by_company.get(e["company_name"], [])
        docs.append("«%s» компаниясы: саласы — %s, жұмыс беруші — %s. Вакансиялары (%d): %s."
                    % (e["company_name"], e["industry"] or "көрсетілмеген", e["full_name"], len(vs),
                       _join(["%s (%s)" % (x["title"], "ашық" if x["status"] == "open" else "жабық") for x in vs])))

    # --- курстар және оларға жазылғандар ---
    enrolled = {}
    for r in q("select c.course_id, u.full_name from enrollments en join courses c on c.course_id = en.course_id "
               "join users u on u.user_id = en.seeker_id where " + _REAL):
        enrolled.setdefault(r["course_id"], []).append(r["full_name"])
    for c in q("select course_id, name, description, duration_hours from courses order by course_id"):
        who = enrolled.get(c["course_id"], [])
        docs.append("«%s» оқу курсы: %s Ұзақтығы %s сағат. Курсқа жазылғандар (%d): %s."
                    % (c["name"], (c["description"] or "").rstrip(".") + ".", c["duration_hours"],
                       len(who), _join(who)))

    # --- жұмыс іздеушілер: білімі, түйіндемесі, өтінімдері, курстары, сәйкестік балдары ---
    apps, courses, matches = {}, {}, {}
    for r in q("select a.seeker_id, v.title, a.status, a.app_date from applications a "
               "join vacancies v on v.vacancy_id = a.vacancy_id order by a.app_date, a.application_id"):
        apps.setdefault(r["seeker_id"], []).append("%s — %s (%s)" % (r["title"], _STATUS[r["status"]], r["app_date"]))
    for r in q("select en.seeker_id, c.name, en.enrolled_at from enrollments en "
               "join courses c on c.course_id = en.course_id order by en.enrolled_at"):
        courses.setdefault(r["seeker_id"], []).append("«%s» (%s)" % (r["name"], r["enrolled_at"]))
    for r in q("select rs.seeker_id, v.title, m.score from match_results m "
               "join resumes rs on rs.resume_id = m.resume_id "
               "join vacancies v on v.vacancy_id = m.vacancy_id order by m.score desc"):
        matches.setdefault(r["seeker_id"], []).append("%s — %d%%" % (r["title"], round(float(r["score"]))))
    for s in q("select u.user_id, u.full_name, js.education, js.skills, r.experience_years, r.experience "
               "from job_seekers js join users u on u.user_id = js.user_id "
               "left join resumes r on r.seeker_id = js.user_id where " + _REAL + " order by u.user_id"):
        uid = s["user_id"]
        docs.append(
            "%s — жұмыс іздеуші: білімі — %s, дағдылары — %s, жұмыс өтілі — %s жыл (%s)."
            % (s["full_name"], s["education"] or "көрсетілмеген", s["skills"] or "көрсетілмеген",
               s["experience_years"] if s["experience_years"] is not None else "көрсетілмеген",
               s["experience"] or "түйіндеме жоқ"))
        docs.append("%s жіберген өтініштер (%d): %s." % (s["full_name"], len(apps.get(uid, [])), _join(apps.get(uid, []))))
        docs.append("%s жазылған оқу курстары: %s." % (s["full_name"], _join(courses.get(uid, []))))
        if matches.get(uid):
            docs.append("%s түйіндемесінің вакансияларға сәйкестік балдары: %s."
                        % (s["full_name"], _join(matches[uid][:5])))

    # --- мамандар мен әкімшілер ---
    for r in q("select u.full_name, s.department from specialists s join users u on u.user_id = s.user_id "
               "where " + _REAL + " order by u.user_id"):
        docs.append("%s — маман, бөлімі: %s." % (r["full_name"], r["department"] or "көрсетілмеген"))
    for r in q("select u.full_name, a.access_level from admins a join users u on u.user_id = a.user_id "
               "where " + _REAL + " order by u.user_id"):
        docs.append("%s — әкімші, қол жеткізу деңгейі: %s (1-ден 5-ке дейін)." % (r["full_name"], r["access_level"]))

    # --- қорытынды статистика ---
    roles = {r["role"]: int(r["n"]) for r in q(
        "select u.role, count(*) as n from users u where " + _REAL + " group by u.role")}
    docs.append("Жүйедегі пайдаланушылар саны: барлығы %d (%s)."
                % (sum(roles.values()), ", ".join("%s — %d" % (_ROLE[k], v) for k, v in roles.items())))
    st = {r["status"]: int(r["n"]) for r in q(
        "select a.status, count(*) as n from applications a join vacancies v on v.vacancy_id = a.vacancy_id "
        "where v.title not like 'Демо%' group by a.status")}
    docs.append("Өтініштер статистикасы: барлығы %d өтініш (%s)."
                % (sum(st.values()), ", ".join("%s — %d" % (_STATUS[k], v) for k, v in st.items())))
    open_n = sum(1 for v in vacancies if v["status"] == "open")
    docs.append("Вакансиялар статистикасы: барлығы %d вакансия, оның ашығы — %d, жабығы — %d."
                % (len(vacancies), open_n, len(vacancies) - open_n))
    if vacancies:
        top = max(vacancies, key=lambda v: float(v["salary"]))
        low = min(vacancies, key=lambda v: float(v["salary"]))
        docs.append("Ең жоғары жалақылы вакансия — %s (%d теңге, «%s»); ең төмен жалақылы — %s (%d теңге, «%s»)."
                    % (top["title"], int(float(top["salary"])), top["company_name"],
                       low["title"], int(float(low["salary"])), low["company_name"]))
        busiest = sorted(vacancies, key=lambda v: -apps_by_vac.get(v["vacancy_id"], 0))[:3]
        docs.append("Ең көп өтініш түскен вакансиялар: %s."
                    % _join(["%s (%d өтініш)" % (v["title"], apps_by_vac.get(v["vacancy_id"], 0)) for v in busiest]))
    return docs


def build_documents(db=None) -> list:
    """Статикалық ережелер + базадан алынған құжаттар. База қолжетімсіз болса, тек ережелер."""
    try:
        if db is None:
            import config
            from data.database import Database
            db = Database(config.connection_string())
        return STATIC_DOCS + db_documents(db)
    except Exception as error:  # база қосылмаса да лаба жұмыс істей берсін
        print("Ескерту: базаға қосыла алмадым (%s). Тек жүйе ережелері қолданылады." % type(error).__name__)
        return list(STATIC_DOCS)
