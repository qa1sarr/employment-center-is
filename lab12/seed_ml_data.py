"""Оқыту үшін демо деректерді ӨЗ базамызға қосады (бар кестелерге: users, resumes, vacancies,
applications, match_results). Демо жазбалар email-і '@ml.demo' аяқталады.
  python seed_ml_data.py          - қосу
  python seed_ml_data.py --clean  - қосылғанды толық өшіру"""
import hashlib
import random
import sys

SKILLS = ["Python", "SQL", "Excel", "1С", "Git", "AutoCAD", "SMM", "Логистика", "Бухгалтерия", "Тестілеу"]
DOMAIN = "@ml.demo"


def clean(db):
    ids = [r["user_id"] for r in db.query("select user_id from users where email like ?", ("%" + DOMAIN,))]
    for uid in ids:
        db.execute("delete from match_results where vacancy_id in (select vacancy_id from vacancies where employer_id = ?)", (uid,))
        db.execute("delete from notifications where user_id = ?", (uid,))
        db.execute("delete from applications where seeker_id = ?", (uid,))
        db.execute("delete from applications where vacancy_id in (select vacancy_id from vacancies where employer_id = ?)", (uid,))
        db.execute("delete from users where user_id = ?", (uid,))
    return len(ids)


def seed(db, seekers=80, vacancies=40, seed_value=42):
    rnd = random.Random(seed_value)
    pw = hashlib.sha256(b"123456").hexdigest()

    def user(name, email, role):
        return db.execute(
            "insert into users (full_name, email, phone, password_hash, role) output inserted.user_id values (?, ?, ?, ?, ?)",
            (name, email, None, pw, role), returns_id=True)

    # демо жұмыс беруші және оның вакансиялары: жалақы талап етілетін өтілге байланысты өседі
    emp = user("ML Demo ТОО", "employer" + DOMAIN, "employer")
    db.execute("insert into employers (user_id, company_name, industry) values (?, ?, ?)", (emp, "ML Demo ТОО", "IT"))
    vacs = []
    for i in range(vacancies):
        req_exp = round(rnd.uniform(0, 12), 1)
        salary = round((200_000 + 27_000 * req_exp + rnd.gauss(0, 18_000)) / 1000) * 1000
        vid = db.execute(
            "insert into vacancies (employer_id, title, requirements, salary, status) output inserted.vacancy_id values (?, ?, ?, ?, 'open')",
            (emp, "Демо вакансия %d" % (i + 1), ", ".join(rnd.sample(SKILLS, 3)), salary), returns_id=True)
        vacs.append((vid, req_exp))

    created = 0
    for i in range(seekers):
        exp = round(rnd.uniform(0, 12), 1)
        uid = user("Демо үміткер %d" % (i + 1), "seeker%d%s" % (i + 1, DOMAIN), "job_seeker")
        skills = ", ".join(rnd.sample(SKILLS, 3))
        db.execute("insert into job_seekers (user_id, education, skills) values (?, ?, ?)", (uid, "Жоғары", skills))
        resume = db.execute(
            "insert into resumes (seeker_id, skills, experience_years, experience) output inserted.resume_id values (?, ?, ?, ?)",
            (uid, skills, int(exp), "Демо тәжірибе"), returns_id=True)
        # 1) өтіліне ең сай вакансияға ӨТІНІМ ҚАБЫЛДАНДЫ (жоғары сәйкестік)
        best = min(vacs, key=lambda v: abs(v[1] - exp))
        # 2) кездейсоқ басқа вакансияға ӨТІНІМ ҚАБЫЛДАНБАДЫ (төмен сәйкестік)
        other = rnd.choice([v for v in vacs if v[0] != best[0]])
        for (vid, _), status, mean, sd in ((best, "accepted", 84, 8), (other, "rejected", 58, 11)):
            db.execute("insert into applications (seeker_id, vacancy_id, status) values (?, ?, ?)", (uid, vid, status))
            score = max(0.0, min(100.0, round(rnd.gauss(mean, sd), 2)))
            db.execute("insert into match_results (resume_id, vacancy_id, score, model_version) values (?, ?, ?, 'v1.0')",
                       (resume, vid, score))
        created += 1
    return {"seekers": created, "vacancies": vacancies}


if __name__ == "__main__":
    import ml_data
    database = ml_data.get_db()
    if "--clean" in sys.argv:
        print("Өшірілді демо пайдаланушылар:", clean(database))
    elif database.query("select count(*) as n from users where email like ?", ("%" + DOMAIN,))[0]["n"]:
        print("Демо деректер бұрын қосылған. Қайта қосу үшін алдымен: python seed_ml_data.py --clean")
    else:
        print("Қосылды:", seed(database))
