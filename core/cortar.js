// ==============================================
// ⚡ MODO FLASH - VELOCIDAD EXTREMA
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');

const PARAMETROS = {
    DURACION_PARTE: 120,
    VELOCIDAD: 1.30
};

async function extraerYEditarSegmento(rutaArchivo, titulo) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('⚡ MODO FLASH ACTIVADO');
        log.aviso('🔥 VELOCIDAD MÁXIMA | SIN COMPRESIÓN INNECESARIA');

        // ==============================================
        // 🚀 COMANDO ULTRA RÁPIDO
        // ==============================================
        
        const comando = ffmpeg(rutaArchivo)
            
            // OPCIONES GLOBALES
            .nativeFramerate()
            .withOption('-threads', '0')       // Todos los núcleos
            .withOption('-nostdin')            // No esperar entrada

            // 🎞️ FILTROS PERO OPTIMIZADOS
            .videoFilters([
                `setpts=1/${PARAMETROS.VELOCIDAD}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(`atempo=${PARAMETROS.VELOCIDAD}`)

            // ==============================================
            // 📦 EL SECRETO: MÉTODO MÁS RÁPIDO
            // ==============================================
            
            .videoCodec('h264')               // Usar codec nativo del sistema
            .addOption('-preset', 'ultrafast') // 🏎️ VELOCIDAD MÁXIMA
            .addOption('-crf', '28')          // Un poco más de compresión = más veloz
            .addOption('-tune', 'fastdecode') // Optimizar para leer rápido
            .addOption('-max_muxing_queue_size', '1024')

            // AUDIO
            .audioCodec('aac')
            .audioBitrate('96k')

            // ✂️ SEGMENTO
            .outputOptions([
                `-f segment`,
                `-segment_time ${PARAMETROS.DURACION_PARTE}`,
                `-reset_timestamps 1`
            ])

            // SALIDA
            .output(path.join(config.CARPETA_TEMPORAL, `${titulo}_%03d.mp4`))
            .outputFormat('mp4');

        // ==============================================
        // EVENTOS
        // ==============================================
        
        comando.on('progress', (progreso) => {
            const por = progreso.percent || 0;
            if (por % 20 === 0) { // Mostrar menos logs = más velocidad
                log.detalle(`⚡ ${por.toFixed(0)}%`);
            }
        });

        comando.on('end', () => {
            log.exito('✅ LISTO! Video procesado a velocidad luz');
            resolve(true);
        });

        comando.on('error', (err) => {
            log.error('ERROR', err);
            reject(err);
        });

        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
