// 🔗 RUTAS Y FUNCIONES PARA PROCESAR ENLACES
const express = require('express');
const fs = require('fs');
const router = express.Router();

// Dependencias del sistema
const log = require('../js/logger');
const config = require('../config');
const { obtenerDuracionVideo } = require('./utilidades');
const { procesarEnlace } = require('../core/descargar');
const { extraerSegmento } = require('../core/cortar');
const { enviarADosCanales } = require('../core/enviar');

router.post('/procesar-enlace', async (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ENLACE');

    try {
        // Verificar datos
        if (!req.body?.enlace || !req.body?.titulo) {
            log.error('Faltan datos: enlace o título');
            return res.json({
                status: 'error',
                mensaje: '❌ Debés ingresar el enlace y el título'
            });
        }

        const { enlace, titulo } = req.body;
        log.info(`Enlace recibido: ${enlace}`);
        log.info(`Título: ${titulo}`);
        log.aviso('Iniciando descarga... Esto puede tardar bastante');

        // Descargar el video
        const rutaVideo = await procesarEnlace(enlace, titulo);
        if (!rutaVideo || !fs.existsSync(rutaVideo)) {
            log.error('Falló la descarga del video');
            return res.json({
                status: 'error',
                mensaje: '❌ No se pudo descargar el video'
            });
        }

        log.exito('Descarga finalizada, iniciando procesamiento...');

        // Obtener datos del video
        const duracionTotal = await obtenerDuracionVideo(rutaVideo);
        const duracionParte = config.CLIP_DURATION || 60;
        const cantidadPartes = Math.ceil(duracionTotal / duracionParte);

        // Generar partes
        const listaPartes = [];
        for (let i = 1; i <= cantidadPartes; i++) {
            try {
                const rutaParte = await extraerSegmento(rutaVideo, i, titulo);
                if (rutaParte) listaPartes.push({ numero: i, ruta: rutaParte });
            } catch (
