// server.js — іске қосу нүктесі
const { createApp } = require('./app');
const db = require('./db');

const PORT = process.env.PORT || 3000;
createApp(db).listen(PORT, () => {
  console.log(`API сервері http://localhost:${PORT} мекенжайында жұмыс істеп тұр`);
});
