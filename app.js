// ==============================================
// 🚀 MALLYCUTS ENTERPRISE
// APP PRINCIPAL
// ==============================================

require('./config/env');
const express = require('express');
const path = require('path');

// Inicializar App
const app = express();

// ==============================================
// ⚙️ MIDDLEWARES GLOBALES
// ==============================================
app.use(express.json({ limit: '500mb' }));
app.use(express.urlencoded({ extended: true, limit: '500mb' }));

// Logger de peticiones
app.use(require('./middlewares/logger/requestLogger'));

// ==============================================
// 📂 ARCHIVOS ESTÁTICOS
// ==============================================
app.use(express.static(path.join(__dirname, 'public')));

// ==============================================
// 🛣️ CARGA DE RUTAS
// ==============================================
app.use('/', require('./routes/index'));
app.use('/api/archivos', require('./routes/archivos.routes'));
app.use('/api/cortar', require('./routes/cortar.routes'));
app.use('/api/upload', require('./routes/upload.routes'));
app.use('/api/telegram', require('./routes/telegram.routes'));

// ==============================================
// ❌ MANEJO DE ERRORES
// ==============================================
app.use(require('./middlewares/error/handler'));

module.exports = app;
