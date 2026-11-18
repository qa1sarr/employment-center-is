"""Тест үшін SQLite адаптері: Database-пен бірдей интерфейс, нақты seed деректерімен.
SQL Server диалектісінің тек OUTPUT INSERTED бөлігі аударылады."""
import hashlib
import os
import re
import sqlite3
from contextlib import contextmanager

ROOT = os.path.join(os.path.dirname(__file__), "..")
SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
  phone TEXT, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK (role IN ('job_seeker','employer','specialist','admin')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE job_seekers (user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE, education TEXT, skills TEXT);
CREATE TABLE employers (user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE, company_name TEXT NOT NULL, industry TEXT);
CREATE TABLE specialists (user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE, department TEXT);
CREATE TABLE admins (user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE, access_level INTEGER NOT NULL DEFAULT 1 CHECK (access_level BETWEEN 1 AND 5));
CREATE TABLE resumes (resume_id INTEGER PRIMARY KEY AUTOINCREMENT, seeker_id INTEGER NOT NULL UNIQUE REFERENCES job_seekers(user_id) ON DELETE CASCADE,
  skills TEXT NOT NULL, experience_years INTEGER NOT NULL DEFAULT 0 CHECK (experience_years >= 0), experience TEXT, updated_at TEXT NOT NULL DEFAULT CURRENT_DATE);
CREATE TABLE vacancies (vacancy_id INTEGER PRIMARY KEY AUTOINCREMENT, employer_id INTEGER NOT NULL REFERENCES employers(user_id) ON DELETE CASCADE,
  title TEXT NOT NULL, requirements TEXT, salary NUMERIC CHECK (salary >= 0), status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','closed')),
  published_at TEXT NOT NULL DEFAULT CURRENT_DATE);
CREATE TABLE applications (application_id INTEGER PRIMARY KEY AUTOINCREMENT, seeker_id INTEGER NOT NULL REFERENCES job_seekers(user_id),
  vacancy_id INTEGER NOT NULL REFERENCES vacancies(vacancy_id) ON DELETE CASCADE, app_date TEXT NOT NULL DEFAULT CURRENT_DATE,
  status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted','reviewed','accepted','rejected')), UNIQUE (seeker_id, vacancy_id));
CREATE TABLE courses (course_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT, duration_hours INTEGER CHECK (duration_hours > 0));
CREATE TABLE enrollments (seeker_id INTEGER NOT NULL REFERENCES job_seekers(user_id) ON DELETE CASCADE, course_id INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
  assigned_by INTEGER REFERENCES specialists(user_id), enrolled_at TEXT NOT NULL DEFAULT CURRENT_DATE, PRIMARY KEY (seeker_id, course_id));
CREATE TABLE match_results (match_id INTEGER PRIMARY KEY AUTOINCREMENT, resume_id INTEGER NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
  vacancy_id INTEGER NOT NULL REFERENCES vacancies(vacancy_id), score NUMERIC NOT NULL CHECK (score BETWEEN 0 AND 100), model_version TEXT, UNIQUE (resume_id, vacancy_id));
CREATE TABLE notifications (notification_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(user_id),
  application_id INTEGER REFERENCES applications(application_id) ON DELETE SET NULL, message TEXT NOT NULL, sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
"""
OUTPUT_RE = re.compile(r"\s+OUTPUT\s+INSERTED\.\w+", re.I)


class _Tx:
    def __init__(self, conn):
        self.conn = conn

    def query(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def execute(self, sql, params=(), returns_id=False):
        cur = self.conn.execute(OUTPUT_RE.sub("", sql), params)
        return cur.lastrowid if returns_id else None


class SqliteDatabase(_Tx):
    def __init__(self):
        super().__init__(sqlite3.connect(":memory:", check_same_thread=False))
        self.conn.executescript(SCHEMA)
        seed = open(os.path.join(ROOT, "database", "02_insert_data.sql"), encoding="utf-8").read()
        seed = re.sub(r"^(USE .*|GO)\s*$", "", seed, flags=re.M).replace("N'", "'")
        self.conn.executescript(seed)
        digest = hashlib.sha256(b"123456").hexdigest()
        self.conn.execute("UPDATE users SET password_hash = ?", (digest,))
        self.conn.commit()

    def execute(self, sql, params=(), returns_id=False):
        result = super().execute(sql, params, returns_id)
        self.conn.commit()
        return result

    @contextmanager
    def transaction(self):
        try:
            yield _Tx(self.conn)
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
