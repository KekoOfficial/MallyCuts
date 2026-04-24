// ==============================================
// 🚀 SERVIDOR PRINCIPAL - MALLYCUTS
// ==============================================

const express = require('express');
const path = require('path');
const fs = require('fs');

// Importación de módulos internos
const log = require('./js/logger');
const config = require('./config');

// ==============================================
// 🚀 INICIALIZACIÓN DEL SERVIDOR
// ==============================================
const app = express();
const PUERTO = config.PUERTO || 3000;

// Middlewares para leer datos
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Carpeta pública (HTML, CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// ==============================================
// 📂 CREAR CARPETAS SI NO EXISTEN
// ==============================================
const carpetas = [
    config.CARPETA_ENTRADA,
    config.CARPETA_TEMPORAL
];

carpetas.forEach(carpeta => {
    if (!fs.existsSync(carpeta)) {
        fs.mkdirSync(carpeta, { recursive: true });
        log.info(`📂 Carpeta creada: ${carpeta}`);
    }
});

// ==============================================
// 🔌 CONEXIÓN DE ROUTERS
// ==============================================

// Ruta principal del proceso completo
app.use('/', require('./routes/archivos'));

// Módulos separados
app.use('/telegram', require('./routes/telegram'));
app.use('/cortar', require('./routes/cortar'));
app.use('/upload', require('./routes/upload'));
app.use('/enlaces', require('./routes/enlaces'));
app.use('/config', require('./routes/config'));

// ==============================================
// 🟢 INICIAR SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    log.separador();
    log.exito('✅ MALLYCUTS ESTÁ ACTIVO Y FUNCIONANDO');
    log.info(`🌐 Accede desde: http://localhost:${PUERTO}`);
    log.info(`⚙️ Modo: Optimizado | Rápido | Seguro`);
    log.separador();
});
