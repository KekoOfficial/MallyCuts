const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const fs = require('fs');
const log = require('../js/logger');
const config = require('../config');

// ==============================================
// ✂️ FUNCIÓN ULTRA RÁPIDA - MODO TURBO
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, numeroParte, titulo) {
    return new Promise((resolve, reject) => {
        try {
            const duracionPorParte = config.DURACION_POR_PARTE || 120;
            const tiempoInicio = (numeroParte - 1) * duracionPorParte;
            
            const nombreSalida = `${titulo}_parte_${numeroParte}.mp4`;
            const rutaSalida = path.join(config.CARPETA_TEMPORAL, nombreSalida);

            log.detalle(`Inicio: ${tiempoInicio}s | Duración: ${duracionPorParte}s`);

            // ==============================================
            // ⚡ MODO TURBO ACTIVADO
            // ==============================================
            let comando = ffmpeg(rutaArchivo)
                .setStartTime(tiempoInicio)
                .duration(duracionPorParte)

                // Velocidad
                .videoFilters(`setpts=${1 / config.VELOCIDAD_VIDEO}*PTS`)
                .audioFilters(`atempo=${config.VELOCIDAD_VIDEO}`)

                // 👇 ESTO ES LA CLAVE: ULTRA RÁPIDO
                .outputOptions([
                    '-c:v libx264',
                    '-preset ultrafast',  // <-- MÁS RÁPIDO POSIBLE
                    '-crf 28',           // Un poco más de compresión = Velocidad
                    '-c:a aac',
                    '-b:a 96k',
                    '-movflags +faststart'
                ])
                .output(rutaSalida);

            // ==============================================
            // 📊 PROGRESO
            // ==============================================
            comando.on('progress', (progreso) => {
                if (progreso.percent) {
                    log.detalle(`Progreso parte ${numeroParte}: ${progreso.percent.toFixed(1)}%`);
                }
            });

            // ==============================================
            // ✅ FINALIZADO
            // ==============================================
            comando.on('end', () => {
                log.exito(`✅ Parte ${numeroParte} lista!`);
                resolve(rutaSalida);
            });

            // ==============================================
            // ❌ ERROR
            // ==============================================
            comando.on('error', (err) => {
                log.error(`❌ Error parte ${numeroParte}`, err.message);
                reject(err);
            });

            comando.run();

        } catch (error) {
            log.error('Error en la función', error);
            reject(error);
        }
    });
}

module.exports = { extraerYEditarSegmento };
