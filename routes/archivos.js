// ==============================================
// 📤 RUTA PRINCIPAL - MALLYCUTS (OPTIMIZADO)
// ==============================================
// NUEVO FLUJO: CORTE RÁPIDO + EDICIÓN POR PARTE
// ==============================================

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Importación de módulos internos
const log = require('../js/logger');
const config = require('../config');
const { obtenerDuracionVideo, formatoDuracion, archivoEsValido, obtenerTamanoArchivoMB } = require('./utilidades');
const { extraerYEditarSegmento } = require('../core/cortar'); // <-- NUEVA FUNCIÓN
const { enviarADosCanales } = require('../core/enviar');

// ==============================================
// 📂 DEFINICIÓN DE RUTAS
// ==============================================
const CARPETA_ENTRADA = config.CARPETA_ENTRADA;
const CARPETA_TEMPORAL = config.CARPETA_TEMPORAL;

// ==============================================
// 📥 CONFIGURACIÓN DE RECEPCIÓN (MULTER)
// ==============================================

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        log.detalle(`Preparando espacio para guardar el archivo...`);
        cb(null, CARPETA_ENTRADA);
    },
    filename: function (req, file, cb) {
        const titulo = req.body.titulo ? req.body.titulo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim() : 'video_sin_titulo';
        const nombreFinal = `${titulo}_${Date.now()}${path.extname(file.originalname)}`;
        log.detalle(`Nombre asignado al archivo: ${nombreFinal}`);
        cb(null, nombreFinal);
    }
});

const fileFilter = (req, file, cb) => {
    const formatosPermitidos = [
        'video/mp4', 'video/mkv', 'video/avi', 'video/mov',
        'video/flv', 'video/wmv', 'video/mpeg', 'video/webm'
    ];
    if (formatosPermitidos.includes(file.mimetype)) {
        log.exito(`Formato de archivo válido: ${file.mimetype}`);
        cb(null, true);
    } else {
        log.error(`Formato no compatible: ${file.mimetype}`);
        cb(new Error('Formato de archivo no permitido'), false);
    }
};

// ⚙️ Límite de subida elevado a 10 GB
const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024 // 10 Gigabytes
    }
}).single('archivo_video');

// ==============================================
// 🚀 RUTA PRINCIPAL DE PROCESAMIENTO
// ==============================================

router.post('/procesar', (req, res) => {
    log.separador();
    log.info('📥 NUEVA SOLICITUD DE PROCESAMIENTO');
    log.aviso('Modo: CORTE RÁPIDO + EDICIÓN POR PARTES');
    log.aviso('Los resultados saldrán mucho más rápido!');

    upload(req, res, async function (err) {
        try {
            // Manejo de error de subida
            if (err) {
                log.error('Error en la subida del archivo', err);
                return res.json({
                    status: 'error',
                    mensaje: `No se pudo subir: ${err.message}`
                });
            }

            // Validación de datos obligatorios
            if (!req.file || !req.body.titulo) {
                log.error('Faltan datos obligatorios (Título o Archivo)');
                return res.json({
                    status: 'error',
                    mensaje: 'Error: Falta colocar el título o seleccionar el video.'
                });
            }

            // Información inicial
            log.info('✅ Datos recibidos correctamente:');
            log.detalle(`Título: ${req.body.titulo}`);
            log.detalle(`Archivo: ${req.file.filename}`);
            log.detalle(`Tamaño: ${(req.file.size / (1024*1024)).toFixed(2)} MB`);

            // Rutas de trabajo
            const rutaOriginal = path.join(CARPETA_ENTRADA, req.file.filename);
            const tituloLimpio = req.body.titulo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();

            // ==============================================
            // 📏 ETAPA: ANÁLISIS Y PROCESO POR PARTES
            // ==============================================
            log.separador();
            log.info('✂️ INICIANDO CORTE Y EDICIÓN');
            log.separador();

            // Obtener duración total
            const duracionTotal = await obtenerDuracionVideo(rutaOriginal);
            log.exito(`Duración total del video: ${formatoDuracion(duracionTotal)}`);

            // Calcular cantidad de partes
            const duracionPorParte = config.DURACION_POR_PARTE || 120;
            const cantidadPartes = Math.ceil(duracionTotal / duracionPorParte);
            log.info(`📋 División: ${cantidadPartes} partes de ${duracionPorParte}s cada una`);

            const partesGeneradas = [];

            // Bucle principal: Cortar y Editar al mismo tiempo
            for (let i = 1; i <= cantidadPartes; i++) {
                log.info(`\n⚙️ Procesando parte ${i} de ${cantidadPartes}`);

                try {
                    // 👇 ESTA FUNCIÓN HACE TODO: CORTA + PONE VELOCIDAD + PONE MARCA
                    const rutaParte = await extraerYEditarSegmento(
                        rutaOriginal,
                        i,
                        tituloLimpio
                    );

                    if (rutaParte && archivoEsValido(rutaParte)) {
                        partesGeneradas.push({
                            numero: i,
                            ruta: rutaParte
                        });
                        log.exito(`Parte ${i} lista | Tamaño: ${obtenerTamanoArchivoMB(rutaParte)}`);
                    } else {
                        throw new Error(`Archivo generado no válido`);
                    }

                } catch (error) {
                    log.error(`Error en parte ${i}`, error);
                }
            }

            // Validación de resultados
            if (partesGeneradas.length === 0) {
                throw new Error('No se pudo generar ninguna parte válida del video.');
            }

            log.exito(`✅ Proceso completado. Generadas ${partesGeneradas.length} partes.`);

            // Limpieza: Eliminar archivo original grande
            if (fs.existsSync(rutaOriginal)) {
                fs.unlinkSync(rutaOriginal);
                log.detalle('🗑️ Archivo original eliminado');
            }

            // ==============================================
            // 📤 ETAPA: ENVÍO A TELEGRAM
            // ==============================================
            log.separador();
            log.info('📤 INICIANDO ENVÍO A CANALES');
            log.separador();

            // Bucle de envío
            for (const parte of partesGeneradas) {
                const mensaje = `
🎬 <b>${tituloLimpio}</b>
📌 Parte ${parte.numero} de ${partesGeneradas.length}
⚡ Velocidad: ${config.VELOCIDAD_VIDEO}x
🔹 ${config.TEXTO_MARCA_AGUA}
                `.trim();

                try {
                    await enviarADosCanales(parte.ruta, mensaje, parte.numero);
                    
                    // Limpieza post-envío
                    if (config.ELIMINAR_ARCHIVOS_AL_TERMINAR && fs.existsSync(parte.ruta)) {
                        fs.unlinkSync(parte.ruta);
                        log.detalle(`🗑️ Parte ${parte.numero} eliminada`);
                    }

                } catch (error) {
                    log.error(`Error al enviar parte ${parte.numero}`, error);
                }

                // Pausa técnica
                await new Promise(resolve => setTimeout(resolve, 3000));
            }

            // ==============================================
            // ✅ FINALIZACIÓN EXITOSA
            // ==============================================
            log.separador();
            log.exito('✅ PROCESO TERMINADO COMPLETAMENTE');
            log.separador();

            return res.json({
                status: 'ok',
                mensaje: `¡Listo! Video procesado y enviado en ${partesGeneradas.length} partes.`
            });

        } catch (errorGeneral) {
            log.error('ERROR CRÍTICO EN EL SISTEMA', errorGeneral);
            return res.json({
                status: 'error',
                mensaje: `Falló el proceso: ${errorGeneral.message}`
            });
        }
    });
});

module.exports = router;
