// db.js — SQL Server қосылымы (Windows аутентификациясы, ODBC Driver 18)
const sql = require('mssql/msnodesqlv8');

const connectionString =
  process.env.DB_CONNECTION ||
  'Driver={ODBC Driver 18 for SQL Server};' +
  'Server=BORIBEK-QAISAR\\BORIBEK;' +
  'Database=EmploymentCenter;' +
  'Trusted_Connection=Yes;' +
  'TrustServerCertificate=Yes;';

let poolPromise = null;

function getPool() {
  if (!poolPromise) {
    poolPromise = new sql.ConnectionPool({ connectionString })
      .connect()
      .catch((err) => {
        poolPromise = null; // келесі сұрауда қайта қосылып көреміз
        throw err;
      });
  }
  return poolPromise;
}

// query(текст, { параметр: мән }) -> { rows, rowsAffected }
async function query(text, params = {}) {
  const pool = await getPool();
  const request = pool.request();
  for (const [name, value] of Object.entries(params)) {
    request.input(name, value);
  }
  const result = await request.query(text);
  return { rows: result.recordset || [], rowsAffected: result.rowsAffected[0] || 0 };
}

// Бірнеше сұранысты бір транзакцияда орындау
async function transaction(work) {
  const pool = await getPool();
  const tx = new sql.Transaction(pool);
  await tx.begin();
  try {
    const run = async (text, params = {}) => {
      const request = new sql.Request(tx);
      for (const [name, value] of Object.entries(params)) request.input(name, value);
      const r = await request.query(text);
      return { rows: r.recordset || [], rowsAffected: r.rowsAffected[0] || 0 };
    };
    const out = await work(run);
    await tx.commit();
    return out;
  } catch (e) {
    try { await tx.rollback(); } catch (_) {}
    throw e;
  }
}

module.exports = { query, transaction };
