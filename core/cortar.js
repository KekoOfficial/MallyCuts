const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const fs = require('fs');
const log = require('../js/logger');
const config = require('../config');

// ==============================================
// ✂️ FUNCIÓN PRINCIPAL: CORTA Y EDITA AL MISMO TIEMPO
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, numeroParte, titulo) {
    return new Promise((resolve, reject) => {
        try {
            const duracionPorParte = config.DURACION_POR_PARTE || 120;
            const tiempoInicio = (numeroParte - 1) * duracionPorParte;
            
            // Nombre del archivo de salida
            const nombreSalida = `${titulo}_parte_${numeroParte}.mp4`;
            const rutaSalida = path.join(config.CARPETA_TEMPORAL, nombreSalida);

            log.detalle(`Inicio: ${tiempoInicio}s | Duración: ${duracionPorParte}s`);

            // ==============================================
            // 🎬 COMANDO FFmpeg OPTIMIZADO (SIN MARCA DE AGUA)
            // ==============================================
            let comando = ffmpeg(rutaArchivo)
                .setStartTime(tiempoInicio)
                .duration(duracionPorParte)

                // 1. VELOCIDAD DE REPRODUCCIÓN
                .videoFilters(`setpts=${1 / config.VELOCIDAD_VIDEO}*PTS`)
                .audioFilters(`atempo=${config.VELOCIDAD_VIDEO}`)

                // Configuración de salida RÁPIDA
                .outputOptions([
                    '-c:v libx264',
                    '-preset fast',      // <-- MÁS RÁPIDO
                    '-crf 23',
                    '-c:a aac',
                    '-b:a 128k',
                    '-movflags +faststart'
                ])
                .output(rutaSalida);

            // ==============================================
            // 📊 SEGUIMIENTO DEL PROGRESO
            // ==============================================
            comando.on('progress', (progreso) => {
                if (progreso.percent) {
                    log.detalle(`Progreso parte ${numeroParte}: ${progreso.percent.toFixed(1)}%`);
                }
            });

            // ==============================================
            // ✅ FINALIZACIÓN EXITOSA
            // ==============================================
            comando.on('end', () => {
                log.exito(`✅ Parte ${numeroParte} generada correctamente`);
                resolve(rutaSalida);
            });

            // ==============================================
            // ❌ ERROR
            // ==============================================
            comando.on('error', (err) => {
                log.error(`❌ Error al procesar parte ${numeroParte}`, err.message);
                reject(err);
            });

            // Ejecutar
            comando.run();

        } catch (error) {
            log.error('Error en la función extraerYEditarSegmento', error);
            reject(error);
        }
    });
}

module.exports = { extraerYEditarSegmento };
