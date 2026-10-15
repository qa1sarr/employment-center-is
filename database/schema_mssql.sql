-- Жұмыспен қамту орталығының ақпараттық жүйесі
-- ЗС №6: реляциялық деректер қоры (Microsoft SQL Server, T-SQL)
-- Негіз: ЗС №4 Class Diagram

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

-- ===================== 2. INSERT =====================

INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
 (N'Айгерім Нұрланова',  N'aigerim@mail.kz', N'+77011112233', N'hash_a1', N'job_seeker'),
 (N'Данияр Сейтқали',    N'daniyar@mail.kz', N'+77012223344', N'hash_a2', N'job_seeker'),
 (N'Мадина Ахметова',    N'madina@mail.kz',  N'+77013334455', N'hash_a3', N'job_seeker'),
 (N'Бақыт Серіков',      N'bakyt@techno.kz', N'+77014445566', N'hash_b1', N'employer'),
 (N'Алия Төлеуова',      N'aliya@market.kz', N'+77015556677', N'hash_b2', N'employer'),
 (N'Ерлан Жақсылықов',   N'erlan@enbek.kz',  N'+77016667788', N'hash_c1', N'specialist'),
 (N'Айдос Әкімов',       N'aidos@enbek.kz',  N'+77017778899', N'hash_d1', N'admin');

INSERT INTO job_seekers (user_id, education, skills) VALUES
 (1, N'Жоғары', N'Python, SQL, Excel'),
 (2, N'Орта арнаулы', N'Сатуды ұйымдастыру, 1С'),
 (3, N'Жоғары', N'Бухгалтерия, Excel');

INSERT INTO employers (user_id, company_name, industry) VALUES
 (4, N'Techno LLP', N'IT'),
 (5, N'Market Plus', N'Сауда');

INSERT INTO specialists (user_id, department) VALUES
 (6, N'Жұмыспен қамту бөлімі');

INSERT INTO admins (user_id, access_level) VALUES
 (7, 5);

INSERT INTO resumes (seeker_id, skills, experience_years, experience) VALUES
 (1, N'Python, SQL, Excel', 2, N'Деректер талдаушысы, 2 жыл'),
 (2, N'Сатуды ұйымдастыру, 1С', 4, N'Сатушы-кеңесші, 4 жыл'),
 (3, N'Бухгалтерия, Excel', 1, N'Көмекші бухгалтер, 1 жыл');

INSERT INTO vacancies (employer_id, title, requirements, salary, status) VALUES
 (4, N'Junior аналитик',   N'Python, SQL',            350000, N'open'),
 (4, N'Web-әзірлеуші',     N'JavaScript, HTML/CSS',   400000, N'open'),
 (5, N'Сатушы-кеңесші',    N'Сату тәжірибесі, 1С',    250000, N'open'),
 (5, N'Бухгалтер',         N'Бухгалтерия, Excel',     300000, N'closed');

INSERT INTO applications (seeker_id, vacancy_id, status) VALUES
 (1, 1, N'submitted'),
 (2, 3, N'submitted'),
 (3, 4, N'rejected'),
 (1, 2, N'submitted');

INSERT INTO courses (name, description, duration_hours) VALUES
 (N'Python негіздері',        N'Бағдарламалауға кіріспе',        72),
 (N'Цифрлық маркетинг',       N'SMM және онлайн-жарнама',        48),
 (N'1С: Бухгалтерия',         N'Есеп жүргізу бағдарламасы',      60);

INSERT INTO enrollments (seeker_id, course_id, assigned_by) VALUES
 (2, 2, 6),
 (3, 3, 6);

INSERT INTO match_results (resume_id, vacancy_id, score, model_version) VALUES
 (1, 1, 92.50, N'v1.0'),
 (1, 2, 61.00, N'v1.0'),
 (2, 3, 88.75, N'v1.0'),
 (3, 4, 85.00, N'v1.0');

INSERT INTO notifications (user_id, application_id, message) VALUES
 (4, 1, N'Junior аналитик вакансиясына жаңа өтінім түсті'),
 (5, 2, N'Сатушы-кеңесші вакансиясына жаңа өтінім түсті'),
 (3, 3, N'Өтінім қабылданбады, оқыту курсы ұсынылады'),
 (4, 4, N'Web-әзірлеуші вакансиясына жаңа өтінім түсті');

-- ===================== 3. UPDATE =====================

-- Өтінім мәртебесін өзгерту
UPDATE applications
SET status = N'reviewed'
WHERE application_id = 1;

-- Вакансия жалақысын көтеру және жабу
UPDATE vacancies
SET salary = 380000
WHERE vacancy_id = 1;

UPDATE vacancies
SET status = N'closed'
WHERE vacancy_id = 3;

-- Пайдаланушының телефонын жаңарту
UPDATE users
SET phone = N'+77019998877'
WHERE user_id = 2;

-- ===================== 4. DELETE =====================

-- Қабылданбаған өтінімді жою (хабарламаның application_id өрісі NULL болады)
DELETE FROM applications
WHERE status = N'rejected';

-- Нақты хабарламаны жою
DELETE FROM notifications
WHERE notification_id = 4;

-- Жабық вакансияны жою: алдымен match_results жазбаларын жоямыз
-- (SQL Server-де бұл FK үшін CASCADE қолданылмаған), өтінімдер CASCADE арқылы жойылады
DELETE FROM match_results
WHERE vacancy_id IN (SELECT vacancy_id FROM vacancies WHERE status = N'closed');

DELETE FROM vacancies
WHERE status = N'closed';

-- ===================== Тексеру =====================

SELECT u.full_name, v.title, a.status, m.score
FROM applications a
JOIN users u         ON u.user_id = a.seeker_id
JOIN vacancies v     ON v.vacancy_id = a.vacancy_id
LEFT JOIN resumes r  ON r.seeker_id = a.seeker_id
LEFT JOIN match_results m ON m.resume_id = r.resume_id AND m.vacancy_id = v.vacancy_id;

--test3

