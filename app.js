// 🚀 SERVIDOR PRINCIPAL - MallyCuts
// Sistema para procesar videos, dividirlos y enviarlos automáticamente

// Importamos las dependencias básicas
const express = require('express');
const path = require('path');

// Importamos sistema de logs
const log = require('./js/logger');

// Cargamos la configuración del proyecto
let config;
try {
    config = require('./config');
    log.exito('Archivo de configuración cargado correctamente');
} catch (error) {
    log.error('No se pudo cargar el archivo de configuración', error);
    process.exit(1);
}

// Importamos las rutas y funciones auxiliares
const rutasArchivos = require('./routes/archivos');
const rutasEnlaces = require('./routes/enlaces');
const { crearCarpetasNecesarias } = require('./routes/utilidades');

// Inicializamos la aplicación
const app = express();
const PUERTO = 3000;

// ==============================================
// CONFIGURACIÓN GENERAL DEL SERVIDOR
// ==============================================

// Ocultamos mensajes internos innecesarios
process.env.DEBUG = '';

// Configuración para soportar datos y archivos grandes
app.use(express.json({ limit: '10000mb' }));
app.use(express.urlencoded({ extended: true, limit: '10000mb' }));

// Servimos los archivos estáticos de la interfaz web
app.use(express.static(path.join(__dirname, 'public')));

// Tiempos de espera ampliados para procesos que pueden tardar mucho
app.use((req, res, next) => {
    req.setTimeout(3600000); // 1 hora de espera máxima
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

// Creamos todas las carpetas necesarias para el funcionamiento
crearCarpetasNecesarias(config);

// ==============================================
// CARGAMOS LAS RUTAS DE FUNCIONALIDAD
// ==============================================
app.use('/', rutasArchivos);
app.use('/', rutasEnlaces);

// ==============================================
// LEVANTAMOS EL SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    log.separador('✅ SERVIDOR INICIADO CORRECTAMENTE');
    log.info(`Dirección de acceso: http://localhost:${PUERTO}`);
    log.info(`Límite máximo de archivos: 10 GB`);
    log.info('Listo para recibir archivos o enlaces para procesar');
    log.separador();
});
