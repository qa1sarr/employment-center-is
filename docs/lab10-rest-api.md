# Лаборатория жұмысы №10. HTTP REST API арқылы компоненттердің өзара әрекеттесуі

**Тақырып:** Жұмыспен қамту орталығының ақпараттық жүйесі

## 1. Мақсаты
Node.js + Express көмегімен SQL Server базасымен жұмыс істейтін REST API жасау, `vacancies` (вакансиялар) ресурсына CRUD операцияларын іске асыру және Postman арқылы тестілеу.

## 2. Құрылымы
```
api/
  package.json     тәуелділіктер: express, mssql, msnodesqlv8
  db.js            SQL Server қосылымы, query() және transaction()
  vacancies.js     CRUD өңдеушілері + тексеру (validation)
  app.js           Express маршруттары
  server.js        сервер іске қосу (порт 3000)
  test/            автоматты тесттер (node --test)
  postman/         Postman collection
```
Қабаттар: клиент (Postman) → Express маршруттары (`app.js`) → өңдеушілер (`vacancies.js`) → `db.js` → SQL Server (`EmploymentCenter`).

## 3. Маршруттар
| Әдіс | URL | Сипаттамасы | Сәтті жауап | Қате |
|---|---|---|---|---|
| GET | /api/vacancies | Барлық вакансия (`?status=open`/`closed` сүзгісі) | 200 | 400 (қате status) |
| GET | /api/vacancies/:id | Бір вакансия | 200 | 400, 404 |
| POST | /api/vacancies | Жаңа вакансия | 201 + `vacancy_id` | 400 |
| PUT | /api/vacancies/:id | Вакансияны жаңарту | 200 | 400, 404 |
| DELETE | /api/vacancies/:id | Вакансияны жою | 200 | 404 |

Қосымша: Node.js 24 LTS қолданылды (`msnodesqlv8` үшін дайын нұсқасы бар), `npm install` кейін `npm install-scripts approve msnodesqlv8` және `npm rebuild msnodesqlv8` орындалады.

Тексеру ережелері: `employer_id` — оң бүтін сан, `title` бос емес, `salary` ≥ 0, `status` — `open` немесе `closed`. Жоқ `employer_id` берілсе SQL Server FK қатесін (547) қайтарады, API оны 400-ге түрлендіреді.
Жою кезінде `match_results` кестесінде CASCADE жоқ болғандықтан, алдымен сол кестедегі жазбалар бір транзакцияда жойылады.

## 4. Іске қосу
```powershell
cd api
npm install
npm start
```
Консольде: `API сервері http://localhost:3000 мекенжайында жұмыс істеп тұр`.
Бастапқы қосылым — Windows аутентификациясы, сервер `BORIBEK-QAISAR\BORIBEK`. Басқа сервер үшін: `$env:DB_CONNECTION = "Driver={ODBC Driver 18 for SQL Server};Server=...;Database=EmploymentCenter;Trusted_Connection=Yes;TrustServerCertificate=Yes;"`.

## 5. Postman арқылы тестілеу
Postman → Import → `api/postman/employment-center.postman_collection.json`.

| № | Сұраныс | Күтілетін нәтиже |
|---|---|---|
| 1 | GET /api/vacancies | 200, JSON массив |
| 2 | GET /api/vacancies?status=open | 200, тек ашық вакансиялар |
| 3 | GET /api/vacancies/1 | 200, бір вакансия |
| 4 | POST /api/vacancies | 201, `{"message":"Вакансия қосылды","vacancy_id":N}` |
| 5 | PUT /api/vacancies/{id} (4-қадамда қосылған id) | 200, «Вакансия жаңартылды» |
| 6 | DELETE /api/vacancies/{id} | 200, «Вакансия сәтті жойылды» |
| 7 | GET /api/vacancies/999 | 404, «Вакансия табылмады» |
| 8 | POST (title жоқ) | 400 |
| 9 | POST (salary = -1) | 400 |
| 10 | POST (employer_id = 99999) | 400 |

4-сұраныс қайтарған `vacancy_id` collection айнымалысына (`{{vacancy_id}}`) автоматты түрде сақталады, 5 және 6-сұраныстар сол жазбамен жұмыс істейді, базадағы бастапқы деректер өзгермейді. Жұмыс берушілер `employer_id` = 4 (базада бар мән). Әр сұранысқа статус-кодты тексеретін Postman тесті қосылған.
Скриншоттарды (кем дегенде 1, 3, 4, 6, 7) есепке қосыңыз.

## 6. Автоматты тесттер
```powershell
cd api
npm test
```
17 тест (барлық статус-кодтар, валидация, FK қатесі, транзакциялық жою) жалған `db` арқылы жүреді, SQL Server керек емес.

## 7. Қорытынды
Жұмыста Express арқылы REST API жасалып, вакансиялар үшін CRUD операциялары SQL Server базасымен байланыстырылды, нәтиже Postman арқылы тексерілді.
