// ==============================================
// 🚀 SERVIDOR PRINCIPAL - MALLYCUTS
// ==============================================

const express = require('express');
const app = express();
const path = require('path');

// Importar configuración
const log = require('./js/logger');

// ==============================================
// ⚙️ MIDDLEWARES
// ==============================================
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Servir archivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// ==============================================
// 📂 CARGAR RUTAS CORRECTAMENTE
// ==============================================
const rutaUpload   = require('./routes/upload');
const rutaProcesar = require('./routes/archivos');

app.use('/upload', rutaUpload);
app.use('/', rutaProcesar);

// ==============================================
// 🚀 INICIAR SERVIDOR
// ==============================================
const PUERTO = 3000;

app.listen(PUERTO, () => {
    log.separador();
    log.exito('✅ MALLYCUTS ESTÁ ACTIVO');
    log.info(`🌐 http://localhost:${PUERTO}`);
    log.aviso('⚡ MODO DIOS 2.0 LISTO');
    log.separador();
});
