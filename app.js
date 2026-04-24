// 🚀 SERVIDOR PRINCIPAL - MallyCuts
// Sistema para procesar videos largos, dividirlos y enviarlos automáticamente

// Importamos las dependencias necesarias
const express = require('express');
const path = require('path');
const fs = require('fs');

// 🔹 Sistema de logs
const log = require('./js/logger');

// 🔹 Cargamos configuración
let config;
try {
    config = require('./config');
    log.exito('Archivo de configuración cargado correctamente');
} catch (error) {
    log.error('No se pudo cargar el archivo de configuración', error);
    process.exit(1);
}

// 🔹 Cargamos módulos de funcionalidad
const rutasArchivos = require('./routes/archivos');
const rutasEnlaces = require('./routes/enlaces');
const utilidades = require('./routes/utilidades');

// Inicializamos la aplicación
const app = express();
const PUERTO = 3000;

// ==============================================
// CONFIGURACIÓN GENERAL
// ==============================================

// Ocultamos mensajes internos
process.env.DEBUG = '';

// Límites ampliados para archivos grandes
app.use(express.json({ limit: '10000mb' }));
app.use(express.urlencoded({ extended: true, limit: '10000mb' }));

// Archivos estáticos de la web
app.use(express.static(path.join(__dirname, 'public')));

// Tiempos de espera largos para procesamientos pesados
app.use((req, res, next) => {
    req.setTimeout(3600000);
    res.setTimeout(3600000);
    res.timeout = 3600000;
    next();
});

// Manejo global de errores
app.use((err, req, res, next) => {
    log.error('Error general en el servidor', err);
    res.status(500).json({
        status: 'error',
        mensaje: '❌ Ocurrió un error inesperado en el servidor'
    });
});

// Creamos carpetas necesarias
utilidades.crearCarpetasNecesarias(config);

// ==============================================
// CARGAMOS LAS RUTAS
// ==============================================
app.use('/', rutasArchivos);
app.use('/', rutasEnlaces);

// ==============================================
// LEVANTAMOS EL SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    log.separador('✅ SERVIDOR INICIADO');
    log.info(`Servidor corriendo en: http://localhost:${PUERTO}`);
    log.info(`Límite máximo de archivos: 10 GB`);
    log.info('Listo para recibir archivos o enlaces');
    log.separador();
});
