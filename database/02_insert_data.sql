USE EmploymentCenter;
GO

INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
 (N'Айгерім Нұрланова', N'aigerim@mail.kz', N'+77011112233', N'hash_1', N'job_seeker'),
 (N'Данияр Сейтқали', N'daniyar@mail.kz', N'+77012223344', N'hash_2', N'job_seeker'),
 (N'Мадина Ахметова', N'madina@mail.kz', N'+77013334455', N'hash_3', N'job_seeker'),
 (N'Бақыт Серіков', N'bakyt@techno.kz', N'+77014445566', N'hash_4', N'employer'),
 (N'Алия Төлеуова', N'aliya@market.kz', N'+77015556677', N'hash_5', N'employer'),
 (N'Ерлан Жақсылықов', N'erlan@enbek.kz', N'+77016667788', N'hash_6', N'specialist'),
 (N'Айдос Әкімов', N'aidos@enbek.kz', N'+77017778899', N'hash_7', N'admin'),
 (N'Арман Қасымов', N'arman@mail.kz', N'+77021110001', N'hash_8', N'job_seeker'),
 (N'Гүлнар Омарова', N'gulnar@mail.kz', N'+77021110002', N'hash_9', N'job_seeker'),
 (N'Нұрсұлтан Беков', N'nursultan@mail.kz', N'+77021110003', N'hash_10', N'job_seeker'),
 (N'Динара Сәдуақасова', N'dinara@mail.kz', N'+77021110004', N'hash_11', N'job_seeker'),
 (N'Жасұлан Тілеуов', N'zhasulan@mail.kz', N'+77021110005', N'hash_12', N'job_seeker'),
 (N'Салтанат Мұратова', N'saltanat@mail.kz', N'+77021110006', N'hash_13', N'job_seeker'),
 (N'Ермек Дәулетов', N'ermek@mail.kz', N'+77021110007', N'hash_14', N'job_seeker'),
 (N'Аружан Қалиева', N'aruzhan@mail.kz', N'+77021110008', N'hash_15', N'job_seeker'),
 (N'Серік Ғабитов', N'serik@qazbuild.kz', N'+77031110001', N'hash_16', N'employer'),
 (N'Томирис Алимова', N'tomiris@medplus.kz', N'+77031110002', N'hash_17', N'employer'),
 (N'Ғалым Рахимов', N'galym@edu-center.kz', N'+77031110003', N'hash_18', N'employer'),
 (N'Әсел Кенжебаева', N'asel@logistika.kz', N'+77031110004', N'hash_19', N'employer'),
 (N'Марат Оспанов', N'marat@bank-kz.kz', N'+77031110005', N'hash_20', N'employer'),
 (N'Назгүл Исмаилова', N'nazgul@enbek.kz', N'+77041110001', N'hash_21', N'specialist'),
 (N'Руслан Байжанов', N'ruslan@enbek.kz', N'+77041110002', N'hash_22', N'specialist'),
 (N'Жанар Сатыбалдиева', N'zhanar@enbek.kz', N'+77041110003', N'hash_23', N'admin');

INSERT INTO job_seekers (user_id, education, skills) VALUES
 (1, N'Жоғары', N'Python, SQL, Excel'),
 (2, N'Орта арнаулы', N'Сатуды ұйымдастыру, 1С'),
 (3, N'Жоғары', N'Бухгалтерия, Excel'),
 (8, N'Жоғары', N'Python, тестілеу, Git'),
 (9, N'Жоғары', N'Медицина, пациентпен жұмыс'),
 (10, N'Жоғары', N'Информатика, педагогика'),
 (11, N'Орта арнаулы', N'Құрылыс, AutoCAD'),
 (12, N'Жоғары', N'Логистика, 1С'),
 (13, N'Жоғары', N'Қаржы, Excel, банк операциялары'),
 (14, N'Орта арнаулы', N'SMM, дизайн, Photoshop'),
 (15, N'Жоғары', N'JavaScript, HTML/CSS, SQL');

INSERT INTO employers (user_id, company_name, industry) VALUES
 (4, N'Techno LLP', N'IT'),
 (5, N'Market Plus', N'Сауда'),
 (16, N'QazBuild', N'Құрылыс'),
 (17, N'MedPlus', N'Медицина'),
 (18, N'Edu Center', N'Білім беру'),
 (19, N'Logistika KZ', N'Логистика'),
 (20, N'Bank KZ', N'Қаржы');

INSERT INTO specialists (user_id, department) VALUES
 (6, N'Жұмыспен қамту бөлімі'),
 (21, N'Кәсіптік бағдарлау бөлімі'),
 (22, N'Оқыту бөлімі');

INSERT INTO admins (user_id, access_level) VALUES
 (7, 5),
 (23, 3);

INSERT INTO resumes (seeker_id, skills, experience_years, experience, updated_at) VALUES
 (1, N'Python, SQL, Excel', 2, N'Деректер талдаушысы, 2 жыл', N'2026-09-01'),
 (2, N'Сатуды ұйымдастыру, 1С', 4, N'Сатушы-кеңесші, 4 жыл', N'2026-09-01'),
 (3, N'Бухгалтерия, Excel', 1, N'Көмекші бухгалтер, 1 жыл', N'2026-09-01'),
 (8, N'Python, тестілеу, Git', 1, N'Стажер-тестілеуші, 1 жыл', N'2026-09-01'),
 (9, N'Медицина, пациентпен жұмыс', 3, N'Медбике, 3 жыл', N'2026-09-01'),
 (10, N'Информатика, педагогика', 5, N'Информатика мұғалімі, 5 жыл', N'2026-09-01'),
 (11, N'Құрылыс, AutoCAD', 6, N'Прораб, 6 жыл', N'2026-09-01'),
 (12, N'Логистика, 1С', 2, N'Диспетчер, 2 жыл', N'2026-09-01'),
 (13, N'Қаржы, Excel, банк операциялары', 3, N'Банк операционисті, 3 жыл', N'2026-09-01'),
 (14, N'SMM, дизайн, Photoshop', 2, N'SMM-маман, 2 жыл', N'2026-09-01'),
 (15, N'JavaScript, HTML/CSS, SQL', 1, N'Junior әзірлеуші, 1 жыл', N'2026-09-01');

INSERT INTO vacancies (employer_id, title, requirements, salary, status, published_at) VALUES
 (4, N'Junior аналитик', N'Python, SQL', 350000, N'open', N'2026-09-01'),
 (4, N'Web-әзірлеуші', N'JavaScript, HTML/CSS', 400000, N'open', N'2026-09-02'),
 (5, N'Сатушы-кеңесші', N'Сату тәжірибесі, 1С', 250000, N'open', N'2026-09-03'),
 (5, N'Бухгалтер', N'Бухгалтерия, Excel', 300000, N'closed', N'2026-08-20'),
 (4, N'Тестілеуші (QA)', N'Тестілеу, Git, SQL', 330000, N'open', N'2026-09-05'),
 (16, N'Құрылыс прорабы', N'Құрылыс, AutoCAD', 450000, N'open', N'2026-09-06'),
 (16, N'Сметашы', N'Смета, Excel', 320000, N'open', N'2026-09-07'),
 (17, N'Медбике', N'Медициналық білім', 280000, N'open', N'2026-09-08'),
 (17, N'Фармацевт', N'Фармацевтикалық білім', 260000, N'closed', N'2026-08-25'),
 (18, N'Информатика мұғалімі', N'Педагогика, информатика', 270000, N'open', N'2026-09-10'),
 (18, N'Әдіскер', N'Педагогика, құжат жүргізу', 240000, N'open', N'2026-09-11'),
 (19, N'Логист', N'Логистика, 1С', 310000, N'open', N'2026-09-12'),
 (19, N'Диспетчер', N'Коммуникация, логистика', 290000, N'open', N'2026-09-13'),
 (20, N'Банк операционисті', N'Қаржы, банк операциялары', 300000, N'open', N'2026-09-14'),
 (20, N'Кредит менеджері', N'Қаржы, талдау', 380000, N'open', N'2026-09-15'),
 (5, N'Маркетолог', N'SMM, жарнама', 340000, N'open', N'2026-09-16');

INSERT INTO applications (seeker_id, vacancy_id, status, app_date) VALUES
 (1, 1, N'submitted', N'2026-09-10'),
 (2, 3, N'submitted', N'2026-09-11'),
 (3, 4, N'rejected', N'2026-09-05'),
 (1, 2, N'submitted', N'2026-09-12'),
 (8, 5, N'submitted', N'2026-09-13'),
 (8, 1, N'reviewed', N'2026-09-13'),
 (9, 8, N'submitted', N'2026-09-14'),
 (9, 9, N'rejected', N'2026-09-01'),
 (10, 10, N'accepted', N'2026-09-15'),
 (10, 11, N'submitted', N'2026-09-15'),
 (11, 6, N'submitted', N'2026-09-16'),
 (11, 7, N'reviewed', N'2026-09-16'),
 (12, 12, N'submitted', N'2026-09-17'),
 (12, 13, N'rejected', N'2026-09-17'),
 (13, 14, N'submitted', N'2026-09-18'),
 (13, 15, N'accepted', N'2026-09-18'),
 (14, 16, N'submitted', N'2026-09-19'),
 (14, 3, N'reviewed', N'2026-09-19'),
 (15, 2, N'submitted', N'2026-09-20'),
 (15, 5, N'submitted', N'2026-09-20'),
 (2, 16, N'submitted', N'2026-09-21'),
 (3, 14, N'rejected', N'2026-09-21'),
 (1, 5, N'reviewed', N'2026-09-22'),
 (9, 10, N'submitted', N'2026-09-22');

INSERT INTO courses (name, description, duration_hours) VALUES
 (N'Python негіздері', N'Бағдарламалауға кіріспе', 72),
 (N'Цифрлық маркетинг', N'SMM және онлайн-жарнама', 48),
 (N'1С: Бухгалтерия', N'Есеп жүргізу бағдарламасы', 60),
 (N'SQL негіздері', N'Деректер қорына кіріспе', 40),
 (N'Web-дизайн негіздері', N'HTML, CSS және макет жасау', 56),
 (N'Ағылшын тілі (A2–B1)', N'Жұмыс орнындағы сөйлесу тілі', 90),
 (N'Excel кеңейтілген курсы', N'Формулалар, кестелер, диаграммалар', 32),
 (N'Қаржылық сауаттылық', N'Бюджет және есеп негіздері', 24),
 (N'Клиентпен жұмыс', N'Қарым-қатынас және сату техникасы', 30),
 (N'Жобаларды басқару', N'Жоспарлау және команда жұмысы', 64);

INSERT INTO enrollments (seeker_id, course_id, assigned_by, enrolled_at) VALUES
 (2, 2, 6, N'2026-09-10'),
 (3, 3, 6, N'2026-09-11'),
 (1, 4, 6, N'2026-09-12'),
 (8, 1, 21, N'2026-09-12'),
 (9, 6, 21, N'2026-09-13'),
 (10, 7, 21, N'2026-09-14'),
 (11, 5, 22, N'2026-09-14'),
 (12, 9, 22, N'2026-09-15'),
 (13, 8, 6, N'2026-09-16'),
 (14, 10, 21, N'2026-09-17'),
 (15, 1, 22, N'2026-09-18'),
 (2, 9, 6, N'2026-09-19'),
 (3, 7, 21, N'2026-09-20'),
 (14, 2, 22, N'2026-09-21');

INSERT INTO match_results (resume_id, vacancy_id, score, model_version) VALUES
 (1, 1, 92.50, N'v1.0'),
 (1, 2, 61.00, N'v1.0'),
 (2, 3, 88.75, N'v1.0'),
 (3, 4, 85.00, N'v1.0'),
 (1, 5, 78.40, N'v1.0'),
 (4, 5, 89.20, N'v1.0'),
 (4, 1, 64.10, N'v1.0'),
 (5, 8, 90.30, N'v1.0'),
 (6, 10, 87.60, N'v1.0'),
 (6, 11, 72.50, N'v1.0'),
 (7, 6, 83.00, N'v1.0'),
 (7, 7, 76.80, N'v1.0'),
 (8, 12, 91.10, N'v1.0'),
 (8, 13, 69.90, N'v1.0'),
 (9, 14, 80.40, N'v1.0'),
 (9, 15, 74.30, N'v1.0'),
 (10, 16, 82.70, N'v1.0'),
 (11, 2, 58.20, N'v1.0'),
 (11, 5, 70.60, N'v1.0'),
 (2, 16, 66.30, N'v1.0'),
 (3, 14, 62.50, N'v1.0'),
 (5, 9, 55.00, N'v1.0');

INSERT INTO notifications (user_id, application_id, message) VALUES
 (4, 1, N'Junior аналитик вакансиясына жаңа өтінім түсті'),
 (5, 2, N'Сатушы-кеңесші вакансиясына жаңа өтінім түсті'),
 (3, 3, N'Өтінім қабылданбады, оқыту курсы ұсынылады'),
 (4, 4, N'Web-әзірлеуші вакансиясына жаңа өтінім түсті'),
 (4, 5, N'Тестілеуші (QA) вакансиясына жаңа өтінім түсті'),
 (4, 6, N'Junior аналитик вакансиясына жаңа өтінім түсті'),
 (17, 7, N'Медбике вакансиясына жаңа өтінім түсті'),
 (9, 8, N'Өтінім қабылданбады, оқыту курсы ұсынылады'),
 (10, 9, N'Құттықтаймыз, өтініміңіз қабылданды'),
 (18, 10, N'Әдіскер вакансиясына жаңа өтінім түсті'),
 (16, 11, N'Құрылыс прорабы вакансиясына жаңа өтінім түсті'),
 (16, 12, N'Сметашы вакансиясына жаңа өтінім түсті'),
 (19, 13, N'Логист вакансиясына жаңа өтінім түсті'),
 (12, 14, N'Өтінім қабылданбады, оқыту курсы ұсынылады'),
 (20, 15, N'Банк операционисті вакансиясына жаңа өтінім түсті'),
 (13, 16, N'Құттықтаймыз, өтініміңіз қабылданды'),
 (5, 18, N'Сатушы-кеңесші вакансиясына жаңа өтінім түсті'),
 (4, 19, N'Web-әзірлеуші вакансиясына жаңа өтінім түсті'),
 (4, 20, N'Тестілеуші (QA) вакансиясына жаңа өтінім түсті'),
 (3, 22, N'Өтінім қабылданбады, оқыту курсы ұсынылады'),
 (1, 23, N'Тестілеуші (QA) вакансиясы бойынша өтінім қаралды');

-- Тексеру: әр кестедегі жол саны
SELECT 'users' AS table_name, COUNT(*) AS row_count FROM users
UNION ALL SELECT 'job_seekers', COUNT(*) FROM job_seekers
UNION ALL SELECT 'employers', COUNT(*) FROM employers
UNION ALL SELECT 'resumes', COUNT(*) FROM resumes
UNION ALL SELECT 'vacancies', COUNT(*) FROM vacancies
UNION ALL SELECT 'applications', COUNT(*) FROM applications
UNION ALL SELECT 'courses', COUNT(*) FROM courses
UNION ALL SELECT 'enrollments', COUNT(*) FROM enrollments
UNION ALL SELECT 'match_results', COUNT(*) FROM match_results
UNION ALL SELECT 'notifications', COUNT(*) FROM notifications;
