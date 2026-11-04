// app.js — Express қосымшасын құру (db сырттан беріледі)
const express = require('express');
const { makeHandlers } = require('./vacancies');

function createApp(db) {
  const app = express();
  app.use(express.json());

  const h = makeHandlers(db);
  app.get('/api/vacancies', h.list);
  app.get('/api/vacancies/:id', h.get);
  app.post('/api/vacancies', h.create);
  app.put('/api/vacancies/:id', h.update);
  app.delete('/api/vacancies/:id', h.remove);

  // Қате JSON келгенде (express.json қатесі) 400 қайтару
  app.use((err, req, res, next) => {
    if (err && err.type === 'entity.parse.failed') return res.status(400).json({ error: 'JSON форматы қате' });
    next(err);
  });
  return app;
}

module.exports = { createApp };
