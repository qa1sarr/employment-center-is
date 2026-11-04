const test = require('node:test');
const assert = require('node:assert');
const { makeHandlers } = require('../vacancies');

function fakeRes() {
  const r = { code: 200, body: undefined };
  r.status = (c) => { r.code = c; return r; };
  r.json = (b) => { r.body = b; return r; };
  return r;
}

// Жалған db: жадтағы вакансиялар тізімі
function fakeDb() {
  const rows = [
    { vacancy_id: 1, employer_id: 1, title: 'Backend әзірлеуші', requirements: 'Python', salary: 500000, status: 'open' },
    { vacancy_id: 2, employer_id: 1, title: 'Бухгалтер', requirements: null, salary: 300000, status: 'closed' },
  ];
  let next = 3;
  const calls = [];
  const exec = async (text, p = {}) => {
    calls.push(text.trim().split(/\s+/).slice(0, 3).join(' '));
    if (p.employer_id === 999) { const e = new Error('fk'); e.number = 547; throw e; }
    if (p.boom) throw new Error('boom');
    if (/^SELECT \* FROM vacancies WHERE status/.test(text.trim())) return { rows: rows.filter(r => r.status === p.status), rowsAffected: 0 };
    if (/^SELECT \* FROM vacancies WHERE vacancy_id/.test(text.trim())) return { rows: rows.filter(r => r.vacancy_id === p.id), rowsAffected: 0 };
    if (/^SELECT \* FROM vacancies/.test(text.trim())) return { rows: [...rows], rowsAffected: 0 };
    if (/^INSERT/.test(text.trim())) { const id = next++; rows.push({ vacancy_id: id, ...p }); return { rows: [{ vacancy_id: id }], rowsAffected: 1 }; }
    if (/^UPDATE/.test(text.trim())) { const r = rows.find(x => x.vacancy_id === p.id); if (r) Object.assign(r, p); return { rows: [], rowsAffected: r ? 1 : 0 }; }
    if (/^DELETE FROM match_results/.test(text.trim())) return { rows: [], rowsAffected: 0 };
    if (/^DELETE FROM vacancies/.test(text.trim())) { const i = rows.findIndex(x => x.vacancy_id === p.id); if (i >= 0) rows.splice(i, 1); return { rows: [], rowsAffected: i >= 0 ? 1 : 0 }; }
    throw new Error('unexpected sql: ' + text);
  };
  return { query: exec, transaction: async (w) => w(exec), calls, rows };
}

const good = { employer_id: 1, title: 'Тестілеуші', requirements: 'SQL', salary: 400000 };

test('GET /api/vacancies -> 200, тізім', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.list({ query: {} }, res);
  assert.strictEqual(res.code, 200); assert.strictEqual(res.body.length, 2);
});
test('GET ?status=open сүзгісі', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.list({ query: { status: 'open' } }, res);
  assert.strictEqual(res.body.length, 1);
});
test('GET ?status=x -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.list({ query: { status: 'x' } }, res);
  assert.strictEqual(res.code, 400);
});
test('GET /1 -> 200', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.get({ params: { id: '1' } }, res);
  assert.strictEqual(res.code, 200); assert.strictEqual(res.body.title, 'Backend әзірлеуші');
});
test('GET /999 -> 404', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.get({ params: { id: '999' } }, res);
  assert.strictEqual(res.code, 404);
});
test('GET /abc -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.get({ params: { id: 'abc' } }, res);
  assert.strictEqual(res.code, 400);
});
test('POST дұрыс дене -> 201 және жаңа id', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: good }, res);
  assert.strictEqual(res.code, 201); assert.strictEqual(res.body.vacancy_id, 3);
});
test('POST title жоқ -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: { employer_id: 1 } }, res);
  assert.strictEqual(res.code, 400);
});
test('POST теріс жалақы -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: { ...good, salary: -5 } }, res);
  assert.strictEqual(res.code, 400);
});
test('POST қате status -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: { ...good, status: 'archived' } }, res);
  assert.strictEqual(res.code, 400);
});
test('POST бос дене (undefined) -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: undefined }, res);
  assert.strictEqual(res.code, 400);
});
test('POST жоқ employer (FK 547) -> 400', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.create({ body: { ...good, employer_id: 999 } }, res);
  assert.strictEqual(res.code, 400);
});
test('PUT /1 -> 200', async () => {
  const db = fakeDb(); const h = makeHandlers(db); const res = fakeRes();
  await h.update({ params: { id: '1' }, body: { ...good, status: 'closed' } }, res);
  assert.strictEqual(res.code, 200); assert.strictEqual(db.rows[0].status, 'closed');
});
test('PUT /999 -> 404', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.update({ params: { id: '999' }, body: good }, res);
  assert.strictEqual(res.code, 404);
});
test('DELETE /2 -> 200, алдымен match_results тазаланады', async () => {
  const db = fakeDb(); const h = makeHandlers(db); const res = fakeRes();
  await h.remove({ params: { id: '2' } }, res);
  assert.strictEqual(res.code, 200); assert.strictEqual(db.rows.length, 1);
  assert.deepStrictEqual(db.calls.slice(0, 2), ['DELETE FROM match_results', 'DELETE FROM vacancies']);
});
test('DELETE /999 -> 404', async () => {
  const h = makeHandlers(fakeDb()); const res = fakeRes();
  await h.remove({ params: { id: '999' } }, res);
  assert.strictEqual(res.code, 404);
});
test('db қатесі -> 500', async () => {
  const db = fakeDb(); db.query = async () => { throw new Error('down'); };
  const h = makeHandlers(db); const res = fakeRes();
  const orig = console.error; console.error = () => {};
  await h.list({ query: {} }, res); console.error = orig;
  assert.strictEqual(res.code, 500);
});
