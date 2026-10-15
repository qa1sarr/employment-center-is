CREATE DATABASE EmploymentCenter;
GO
USE EmploymentCenter;
GO

-- ===================== 1. CREATE TABLE =====================

CREATE TABLE users (
    user_id       INT IDENTITY(1,1) PRIMARY KEY,
    full_name     NVARCHAR(100) NOT NULL,
    email         NVARCHAR(100) NOT NULL UNIQUE,
    phone         NVARCHAR(20),
    password_hash NVARCHAR(255) NOT NULL,
    role          NVARCHAR(20)  NOT NULL
                  CHECK (role IN ('job_seeker', 'employer', 'specialist', 'admin')),
    created_at    DATETIME2    NOT NULL DEFAULT SYSDATETIME()
);

CREATE TABLE job_seekers (
    user_id   INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    education NVARCHAR(100),
    skills    NVARCHAR(MAX)
);

CREATE TABLE employers (
    user_id      INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    company_name NVARCHAR(150) NOT NULL,
    industry     NVARCHAR(100)
);

CREATE TABLE specialists (
    user_id    INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    department NVARCHAR(100)
);

CREATE TABLE admins (
    user_id      INT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    access_level INT NOT NULL DEFAULT 1
                 CHECK (access_level BETWEEN 1 AND 5)
);

CREATE TABLE resumes (
    resume_id        INT IDENTITY(1,1) PRIMARY KEY,
    seeker_id        INT NOT NULL UNIQUE REFERENCES job_seekers(user_id) ON DELETE CASCADE,
    skills           NVARCHAR(MAX)    NOT NULL,
    experience_years INT NOT NULL DEFAULT 0 CHECK (experience_years >= 0),
    experience       NVARCHAR(MAX),
    updated_at       DATE    NOT NULL DEFAULT CAST(GETDATE() AS DATE)
);

CREATE TABLE vacancies (
    vacancy_id   INT IDENTITY(1,1) PRIMARY KEY,
    employer_id  INT NOT NULL REFERENCES employers(user_id) ON DELETE CASCADE,
    title        NVARCHAR(150) NOT NULL,
    requirements NVARCHAR(MAX),
    salary       NUMERIC(12, 2) CHECK (salary >= 0),
    status       NVARCHAR(20) NOT NULL DEFAULT 'open'
                 CHECK (status IN ('open', 'closed')),
    published_at DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE)
);

CREATE TABLE applications (
    application_id INT IDENTITY(1,1) PRIMARY KEY,
    seeker_id      INT NOT NULL REFERENCES job_seekers(user_id),
    vacancy_id     INT NOT NULL REFERENCES vacancies(vacancy_id) ON DELETE CASCADE,
    app_date       DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    status         NVARCHAR(20) NOT NULL DEFAULT 'submitted'
                   CHECK (status IN ('submitted', 'reviewed', 'accepted', 'rejected')),
    UNIQUE (seeker_id, vacancy_id)
);

CREATE TABLE courses (
    course_id      INT IDENTITY(1,1) PRIMARY KEY,
    name           NVARCHAR(150) NOT NULL,
    description    NVARCHAR(MAX),
    duration_hours INT CHECK (duration_hours > 0)
);

CREATE TABLE enrollments (
    seeker_id   INT NOT NULL REFERENCES job_seekers(user_id) ON DELETE CASCADE,
    course_id   INT NOT NULL REFERENCES courses(course_id) ON DELETE CASCADE,
    assigned_by INT REFERENCES specialists(user_id),
    enrolled_at DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
    PRIMARY KEY (seeker_id, course_id)
);

CREATE TABLE match_results (
    match_id      INT IDENTITY(1,1) PRIMARY KEY,
    resume_id     INT NOT NULL REFERENCES resumes(resume_id) ON DELETE CASCADE,
    vacancy_id    INT NOT NULL REFERENCES vacancies(vacancy_id),
    score         NUMERIC(5, 2) NOT NULL CHECK (score BETWEEN 0 AND 100),
    model_version NVARCHAR(20),
    UNIQUE (resume_id, vacancy_id)
);

CREATE TABLE notifications (
    notification_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id         INT NOT NULL REFERENCES users(user_id),
    application_id  INT REFERENCES applications(application_id) ON DELETE SET NULL,
    message         NVARCHAR(MAX) NOT NULL,
    sent_at         DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
