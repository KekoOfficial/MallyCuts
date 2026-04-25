// ==============================================
// 🚀 SERVIDOR PRINCIPAL - MALLYCUTS
// ==============================================

const express = require('express');
const router = express.Router();
const app = express();
const path = require('path');

// Importar módulos
const log = require('./js/logger');
const config = require('./config');

// ==============================================
// ⚙️ MIDDLEWARES
// ==============================================
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos (CSS, JS, HTML)
app.use(express.static(path.join(__dirname, 'public')));

// ==============================================
// 📂 CARGAR RUTAS
// ==============================================
const rutaUpload = require('./routes/upload');
const rutaProcesar = require('./routes/archivos');
const rutaConfig = require('./routes/config');

// ✅ AQUÍ ESTABA EL ERROR: ASÍ SE PONE BIEN
app.use('/upload', rutaUpload);
app.use('/', rutaProcesar);   // -> Aquí está tu /procesar
app.use('/config', rutaConfig);

// ==============================================
// 🚀 INICIAR SERVIDOR
// ==============================================
const PUERTO = 3000;

app.listen(PUERTO, () => {
    log.separador();
    log.exito('✅ MALLYCUTS ESTÁ ACTIVO Y FUNCIONANDO');
    log.info(`🌐 Accede desde: http://localhost:${PUERTO}`);
    log.aviso('⚙️ Modo: OPTIMIZADO | RÁPIDO | SEGURO');
    log.separador();
});
