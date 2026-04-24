// 📤 RUTAS Y FUNCIONES PARA PROCESAR ARCHIVOS SUBIDOS
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const router = express.Router();

// Dependencias del sistema
const log = require('../js/logger');
const config = require('../config');
const { obtenerDuracionVideo } = require('./utilidades');
const { extraerSegmento } = require('../core/cortar');
const { enviarADosCanales } = require('../core/enviar');

// ==============================================
// CONFIGURACIÓN DE SUBIDA DE ARCHIVOS
// ==============================================
const almacenamiento = multer.diskStorage({
    destination: (req, archivo, callback) => {
        log.detalle('Preparando espacio para guardar el archivo...');
        callback(null, config.INPUT_FOLDER);
    },
    filename: (req, archivo, callback) => {
        let titulo = req.body.titulo?.trim() || 'video_sin_titulo';
        titulo = titulo.replace(/[<>:"/\\|?*\n\r]/g, ' ').substring(0, 100);
        const nombreFinal = `${titulo}_${Date.now()}.mp4`;
        log.detalle(`Nombre asignado: ${nombreFinal}`);
        callback(null, nombreFinal);
    }
});

const filtroArchivos = (req, archivo, callback) => {
    const formatosPermitidos = ['video/mp4', 'video/mkv', 'video/avi', 'video/mov', 'video/flv', 'video/wmv'];
    if (formatosPermitidos.includes(archivo.mimetype)) {
        log.exito(`Formato válido: ${archivo.mimetype}`);
        callback(null, true);
    } else {
        log.error(`Formato no permitido: ${archivo.mimetype}`);
        callback(new Error('Formato de archivo no permitido'), false);
    }
};

const subirArchivo = multer({
    storage: almacenamiento,
    fileFilter: filtroArchivos,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024,
        parts: 100,
        headerPairs: 2000
    }
}).single('archivo_video');

// ==============================================
// RUTA PRINCIPAL DE PROCESAMIENTO
// ==============================================
router.post('/procesar', (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ARCHIVO');
    log.aviso('Los videos largos pueden tardar bastante tiempo, tené paciencia');

    subirArchivo(req, res, async (errorSubida) => {
        try {
            // Errores al subir
            if (errorSubida) {
                log.error('Error al subir el archivo', errorSubida);
                let mensaje = `❌ No se pudo subir: ${errorSubida.message}`;
                if (errorSubida.code === 'LIMIT_FILE_SIZE') {
                    mensaje = `❌ El archivo supera los 10 GB de límite`;
                }
                return res.json({ status: 'error', mensaje });
            }

            // Verificar datos recibidos
            if (!req.body?.titulo || !req.file) {
                log.error('Faltan datos: título o archivo');
                return res.json({
                    status: 'error',
                    mensaje: '❌ Debés ingresar título y seleccionar un archivo'
                });
            }

            // Mostrar información
            const tamañoGB = (req.file.size / (1024 * 1024 * 1024)).toFixed(2);
            log.info('Datos recibidos:');
            log.detalle(`Título: ${req.body.titulo}`);
            log.detalle(`Tamaño: ${tamañoGB} GB`);

            const tituloVideo = req.body.titulo.trim();
            const rutaOriginal = path.join(config.INPUT_FOLDER, req.file.filename);

            // Verificar que se guardó bien
            if (!fs.existsSync(rutaOriginal)) {
                log.error('El archivo no se guardó correctamente');
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo guardar el archivo en el servidor'
                });
            }

            // Obtener duración
            log.info('Analizando video...');
            const duracionTotal = await obtenerDuracionVideo(rutaOriginal);
            const horas = Math.floor(duracionTotal / 3600);
            const minutos = Math.floor((duracionTotal % 3600) / 60);
            const segundos = Math.floor(duracionTotal % 60);
            log.exito(`Duración total: ${horas}h ${minutos}m ${segundos}s`);

            // Calcular cantidad de partes
            const duracionParte = config.CLIP_DURATION || 60;
            const cantidadPartes = Math.ceil(duracionTotal / duracionParte);
            log.info(`Se generarán ${cantidadPartes} partes de ${duracionParte} segundos cada una`);

            // Generar partes
            const listaPartes = [];
            for (let numParte = 1; numParte <= cantidadPartes; numParte++) {
                log.info(`🔹 Procesando parte ${numParte}/${cantidadPartes}`);
                try {
                    const rutaParte = await extraerSegmento(rutaOriginal, numParte, tituloVideo);
                    if (rutaParte) listaPartes.push({ numero: numParte, ruta: rutaParte });
                } catch (error) {
                    log.error(`No se pudo generar la parte ${numParte}`, error);
                }
            }

            if (listaPartes.length === 0) {
                log.error('No se generó ninguna parte');
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo dividir el video'
                });
            }

            log.exito(`✅ Generadas ${listaPartes.length} partes correctamente`);

            // Enviar partes
            log.info('📤 Enviando archivos a Telegram...');
            for (const parte of listaPartes) {
                const mensaje = `🎬 <b>${tituloVideo}</b>\n📌 Parte ${parte.numero} de ${listaPartes.length}\n⏱️ Duración: ${duracionParte} segundos`;
                
                try {
                    await enviarADosCanales(parte.ruta, mensaje, parte.numero);
                    log.exito(`Parte ${parte.numero} enviada`);
                } catch (error) {
                    log.error(`No se pudo enviar la parte ${parte.numero}`, error);
                }

                // Eliminar archivo temporal
                if (fs.existsSync(parte.ruta)) fs.unlinkSync(parte.ruta);
                await new Promise(resolve => setTimeout(resolve, 3000));
            }

            // Eliminar archivo original
            if (config.BORRAR_ARCHIVO_ORIGINAL !== false && fs.existsSync(rutaOriginal)) {
                fs.unlinkSync(rutaOriginal);
                log.detalle('Archivo original eliminado');
            }

            log.separador('✅ PROCESO FINALIZADO');
            return res.json({
                status: 'ok',
                mensaje: `✅ Procesado correctamente. Se enviaron ${listaPartes.length} partes.`
            });

        } catch (errorGeneral) {
            log.error('Error general', errorGeneral);
            return res.json({
                status: 'error',
                mensaje: `❌ Error: ${errorGeneral.message}`
            });
        }
    });
});

module.exports = router;
