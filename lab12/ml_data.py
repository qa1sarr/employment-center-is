"""Lab 12: деректерді ӨЗ деректер қорымыздан (EmploymentCenter) алу."""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

SALARY_SQL = (
    "select r.experience_years as experience_years, r.skills as skills, v.salary as salary "
    "from applications a "
    "join resumes r on r.seeker_id = a.seeker_id "
    "join vacancies v on v.vacancy_id = a.vacancy_id "
    "where a.status = 'accepted'"
)
HIRING_SQL = (
    "select r.experience_years as experience_years, m.score as match_score, "
    "case when a.status = 'accepted' then 1 else 0 end as hired "
    "from applications a "
    "join resumes r on r.seeker_id = a.seeker_id "
    "join match_results m on m.resume_id = r.resume_id and m.vacancy_id = a.vacancy_id "
    "where a.status in ('accepted', 'rejected')"
)


def get_db():
    import config
    from data.database import Database
    return Database(config.connection_string())


def _frame(db, sql):
    df = pd.DataFrame(db.query(sql))
    return df.astype(float)


def load_salary(db=None):
    """x1 = experience_years (өтіл), x2 = skills_count (түйіндемедегі дағдылар саны), y = salary."""
    df = pd.DataFrame((db or get_db()).query(SALARY_SQL))
    df["skills_count"] = df["skills"].str.count(",") + 1      # "Python, SQL, Git" -> 3
    df = df[["experience_years", "skills_count", "salary"]]
    return df.astype(float)


def load_hiring(db=None):
    """x = experience_years, match_score; y = hired (1 - accepted, 0 - rejected)."""
    df = _frame(db or get_db(), HIRING_SQL)
    df["hired"] = df["hired"].astype(int)
    return df
