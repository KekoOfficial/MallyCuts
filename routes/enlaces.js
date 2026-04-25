// ==============================================
// 📂 GESTOR DE RUTAS - MALLYCUTS
// ==============================================
// Aquí se organizan y exportan todas las rutas
// ==============================================

const express = require('express');
const router = express.Router();

// ==============================================
// 📥 IMPORTAR RUTAS INDIVIDUALES
// ==============================================
const rutaUpload   = require('./upload');   // Subir archivos
const rutaProcesar = require('./archivos'); // Procesar / Enviar
const rutaTitulo   = require('./titulo');   // Generar títulos
const rutaTelegram = require('./telegram'); // Funciones Telegram

// ==============================================
// 🔗 CONECTAR LAS RUTAS
// ==============================================

// 📤 Ruta para subir archivos al servidor
router.use('/upload', rutaUpload);

// 🎬 Ruta principal de procesamiento (donde está el /procesar)
router.use('/', rutaProcesar);

// 📛 Ruta utilitaria para títulos (opcional, por si la usas desde web)
router.use('/titulo', rutaTitulo);

// ==============================================
// 📦 EXPORTAR PARA USAR EN APP.JS
// ==============================================
module.exports = router;
