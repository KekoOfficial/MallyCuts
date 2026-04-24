// 📤 RUTAS Y FUNCIONES PARA PROCESAR ARCHIVOS SUBIDOS
// Versión optimizada para archivos pesados y alta velocidad

const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Importamos módulos internos
const log = require('../js/logger');
const config = require('../config');
const { obtenerDuracionVideo, formatoDuracion, archivoEsValido, obtenerTamanoArchivoMB } = require('./utilidades');
const { extraerSegmento } = require('../core/cortar');
const { enviarADosCanales } = require('../core/enviar');

// ==============================================
// 💡 CONFIGURACIÓN DE CARPETAS
// ==============================================
const CARPETA_ENTRADA = config.CARPETA_ENTRADA;
const CARPETA_TEMPORAL = config.CARPETA_TEMPORAL;

// ==============================================
// 📥 CONFIGURACIÓN DE MULTER
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
    const formatosPermitidos = ['video/mp4', 'video/mkv', 'video/avi', 'video/mov', 'video/flv', 'video/wmv', 'video/mpeg', 'video/webm'];
    if (formatosPermitidos.includes(file.mimetype)) {
        log.exito(`Formato de archivo válido: ${file.mimetype}`);
        cb(null, true);
    } else {
        log.error(`Formato no permitido: ${file.mimetype}`);
        cb(new Error('Formato de archivo no permitido'), false);
    }
};

// ⚙️ LÍMITE DE SUBIDA CONFIGURADO A 10 GB
const upload = multer({
    storage: storage,
    fileFilter: fileFilter,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024 // 10 GB
    }
}).single('archivo_video');

// ==============================================
// 🚀 RUTA PRINCIPAL DE PROCESAMIENTO
// ==============================================

router.post('/procesar', (req, res) => {
    log.separador();
    log.info('📥 NUEVA SOLICITUD DE PROCESAMIENTO');
    log.aviso('Los videos largos pueden tardar varios minutos o incluso horas en procesarse. Tené paciencia.');

    upload(req, res, async function (err) {
        try {
            // Manejo de errores de subida
            if (err) {
                log.error('Error al subir el archivo', err);
                return res.json({
                    status: 'error',
                    mensaje: `No se pudo subir el archivo: ${err.message}`
                });
            }

            // Verificar datos obligatorios
            if (!req.file || !req.body.titulo) {
                log.error('Faltan datos obligatorios');
                return res.json({
                    status: 'error',
                    mensaje: 'Falta el título o el archivo de video'
                });
            }

            log.info('✅ Datos recibidos correctamente:');
            log.detalle(`Título del video: ${req.body.titulo}`);
            log.detalle(`Nombre del archivo: ${req.file.filename}`);
            log.detalle(`Tamaño del archivo: ${(req.file.size / (1024*1024)).toFixed(2)} MB`);

            // Ruta del archivo original
            const rutaOriginal = path.join(CARPETA_ENTRADA, req.file.filename);
            const tituloLimpio = req.body.titulo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();

            // Obtener duración total
            log.info('🔍 Analizando archivo para obtener información...');
            const duracionTotal = await obtenerDuracionVideo(rutaOriginal);
            log.exito(`Duración total del video: ${formatoDuracion(duracionTotal)}`);

            // Calcular cantidad de partes
            const duracionPorParte = config.DURACION_POR_PARTE || 120;
            const cantidadPartes = Math.ceil(duracionTotal / duracionPorParte);
            log.info(`📋 Se dividirá el video en ${cantidadPartes} partes de ${duracionPorParte} segundos cada una`);

            // ==============================================
            // ✂️ INICIO DE CORTE Y PROCESAMIENTO
            // ==============================================
            log.separador();
            log.info('✂️ INICIANDO CORTE Y PROCESAMIENTO DE PARTES');
            log.separador();

            const partesGeneradas = [];

            for (let i = 1; i <= cantidadPartes; i++) {
                log.info(`\n⚙️ Procesando parte ${i} de ${cantidadPartes}`);

                try {
                    const rutaParte = await extraerSegmento(
                        rutaOriginal,
                        i,
                        tituloLimpio
                    );

                    if (rutaParte && archivoEsValido(rutaParte)) {
                        partesGeneradas.push({
                            numero: i,
                            ruta: rutaParte
                        });
                        log.exito(`Parte ${i} generada correctamente | Tamaño: ${obtenerTamanoArchivoMB(rutaParte)}`);
                    } else {
                        throw new Error(`El archivo generado para la parte ${i} no es válido`);
                    }

                } catch (error) {
                    log.error(`Error al procesar la parte ${i}`, error);
                }
            }

            // Verificar si se generaron partes
            if (partesGeneradas.length === 0) {
                throw new Error('No se pudo generar ninguna parte válida del video');
            }

            log.exito(`\n✅ Proceso de corte finalizado. Generadas ${partesGeneradas.length} partes válidas`);

            // ==============================================
            // 📤 ENVÍO A TELEGRAM
            // ==============================================
            log.separador();
            log.info('📤 INICIANDO ENVÍO A LOS CANALES DE TELEGRAM');
            log.separador();

            for (const parte of partesGeneradas) {
                const mensaje = `
🎬 <b>${tituloLimpio}</b>
📌 Parte ${parte.numero} de ${partesGeneradas.length}
⚡ Velocidad: ${config.VELOCIDAD_VIDEO}x
🔹 ${config.TEXTO_MARCA_AGUA}
                `.trim();

                try {
                    await enviarADosCanales(parte.ruta, mensaje, parte.numero);
                    
                    // Borrar archivo temporal
                    if (config.ELIMINAR_ARCHIVOS_AL_TERMINAR && fs.existsSync(parte.ruta)) {
                        fs.unlinkSync(parte.ruta);
                        log.detalle(`🗑️ Archivo temporal de la parte ${parte.numero} eliminado`);
                    }

                } catch (error) {
                    log.error(`Error al enviar la parte ${parte.numero}`, error);
                }

                // Pausa entre envíos para estabilidad
                await new Promise(resolve => setTimeout(resolve, 3000));
            }

            // Borrar archivo original
            if (config.ELIMINAR_ARCHIVOS_AL_TERMINAR && fs.existsSync(rutaOriginal)) {
                fs.unlinkSync(rutaOriginal);
                log.detalle(`🗑️ Archivo original eliminado del sistema`);
            }

            // ==============================================
            // ✅ FINALIZACIÓN
            // ==============================================
            log.separador();
            log.exito('✅ PROCESO COMPLETADO CON ÉXITO');
            log.separador();

            return res.json({
                status: 'ok',
                mensaje: `¡Listo! Se procesaron y enviaron ${partesGeneradas.length} partes correctamente.`
            });

        } catch (errorGeneral) {
            log.error('Error general en el proceso', errorGeneral);
            return res.json({
                status: 'error',
                mensaje: `Ocurrió un error: ${errorGeneral.message}`
            });
        }
    });
});

module.exports = router;
