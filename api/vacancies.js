// vacancies.js — /api/vacancies маршруттарының өңдеушілері.
// db сырттан беріледі (dependency injection), сондықтан тестте жалған db қолдануға болады.

const STATUSES = ['open', 'closed'];

function parseId(raw) {
  const n = Number(raw);
  return Number.isInteger(n) && n > 0 ? n : null;
}

// Денені тексеру. partial=false: POST/PUT үшін барлық міндетті өрістер керек.
function validate(body) {
  const errors = [];
  const b = body || {};
  if (!Number.isInteger(b.employer_id) || b.employer_id <= 0) errors.push('employer_id оң бүтін сан болуы керек');
  if (typeof b.title !== 'string' || b.title.trim() === '') errors.push('title бос болмауы керек');
  if (b.requirements !== undefined && b.requirements !== null && typeof b.requirements !== 'string')
    errors.push('requirements мәтін болуы керек');
  if (b.salary !== undefined && b.salary !== null && (typeof b.salary !== 'number' || b.salary < 0))
    errors.push('salary теріс емес сан болуы керек');
  if (b.status !== undefined && !STATUSES.includes(b.status)) errors.push("status 'open' немесе 'closed' болуы керек");
  return errors;
}

function makeHandlers(db) {
  const fail = (res, err) => {
    if (err && err.number === 547) // сыртқы кілт (FK) бұзылды
      return res.status(400).json({ error: 'Байланысты жазба табылмады (employer_id қате) немесе жазба басқа кестелермен байланысты' });
    console.error(err);
    return res.status(500).json({ error: 'Сервер қатесі' });
  };

  return {
    async list(req, res) {
      try {
        const { status } = req.query || {};
        if (status !== undefined && !STATUSES.includes(status))
          return res.status(400).json({ error: "status 'open' немесе 'closed' болуы керек" });
        const r = status
          ? await db.query('SELECT * FROM vacancies WHERE status = @status ORDER BY vacancy_id', { status })
          : await db.query('SELECT * FROM vacancies ORDER BY vacancy_id');
        res.status(200).json(r.rows);
      } catch (e) { fail(res, e); }
    },

    async get(req, res) {
      try {
        const id = parseId(req.params.id);
        if (id === null) return res.status(400).json({ error: 'id оң бүтін сан болуы керек' });
        const r = await db.query('SELECT * FROM vacancies WHERE vacancy_id = @id', { id });
        if (r.rows.length === 0) return res.status(404).json({ error: 'Вакансия табылмады' });
        res.status(200).json(r.rows[0]);
      } catch (e) { fail(res, e); }
    },

    async create(req, res) {
      try {
        const errors = validate(req.body);
        if (errors.length) return res.status(400).json({ error: errors.join('; ') });
        const { employer_id, title, requirements = null, salary = null, status = 'open' } = req.body;
        const r = await db.query(
          `INSERT INTO vacancies (employer_id, title, requirements, salary, status)
           OUTPUT INSERTED.vacancy_id
           VALUES (@employer_id, @title, @requirements, @salary, @status)`,
          { employer_id, title: title.trim(), requirements, salary, status }
        );
        res.status(201).json({ message: 'Вакансия қосылды', vacancy_id: r.rows[0].vacancy_id });
      } catch (e) { fail(res, e); }
    },

    async update(req, res) {
      try {
        const id = parseId(req.params.id);
        if (id === null) return res.status(400).json({ error: 'id оң бүтін сан болуы керек' });
        const errors = validate(req.body);
        if (errors.length) return res.status(400).json({ error: errors.join('; ') });
        const { employer_id, title, requirements = null, salary = null, status = 'open' } = req.body;
        const r = await db.query(
          `UPDATE vacancies
              SET employer_id = @employer_id, title = @title, requirements = @requirements,
                  salary = @salary, status = @status
            WHERE vacancy_id = @id`,
          { id, employer_id, title: title.trim(), requirements, salary, status }
        );
        if (r.rowsAffected === 0) return res.status(404).json({ error: 'Вакансия табылмады' });
        res.status(200).json({ message: 'Вакансия жаңартылды' });
      } catch (e) { fail(res, e); }
    },

    async remove(req, res) {
      try {
        const id = parseId(req.params.id);
        if (id === null) return res.status(400).json({ error: 'id оң бүтін сан болуы керек' });
        // match_results кестесінде CASCADE жоқ, сондықтан алдымен соны тазалаймыз
        const affected = await db.transaction(async (run) => {
          await run('DELETE FROM match_results WHERE vacancy_id = @id', { id });
          const d = await run('DELETE FROM vacancies WHERE vacancy_id = @id', { id });
          return d.rowsAffected;
        });
        if (affected === 0) return res.status(404).json({ error: 'Вакансия табылмады' });
        res.status(200).json({ message: 'Вакансия сәтті жойылды' });
      } catch (e) { fail(res, e); }
    },
  };
}

module.exports = { makeHandlers, validate, parseId };
