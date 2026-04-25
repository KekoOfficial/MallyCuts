// ==============================================
// ⚡ MODO MISIL - VELOCIDAD MÁXIMA TERMUX
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
        log.inicio('⚡ MODO MISIL ACTIVADO');
        log.aviso('🔥 VELOCIDAD EXTREMA | SIN PERDER TIEMPO');

        const comando = ffmpeg(rutaArchivo)
            
            // 🔧 OPCIONES RÁPIDAS
            .nativeFramerate()
            .withOption('-threads', '0')
            .withOption('-nostdin')

            // 🎬 FILTROS (Solo lo necesario)
            .videoFilters([
                `setpts=1/${PARAMETROS.VELOCIDAD}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(`atempo=${PARAMETROS.VELOCIDAD}`)

            // ==============================================
            // 🚀 LA MAGIA: MÁS RÁPIDO IMPOSIBLE
            // ==============================================
            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')    // 🏎️ VELOCIDAD MÁXIMA
            .addOption('-crf', '30')             // Menos calidad = Mucho más rápido
            .addOption('-tune', 'fastdecode')    // Optimizar lectura
            .addOption('-max_muxing_queue_size', '1024')

            // 🎧 AUDIO LIGERO
            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1) // Mono = Más rápido

            // ✂️ CORTE
            .outputOptions([
                `-f segment`,
                `-segment_time ${PARAMETROS.DURACION_PARTE}`,
                `-reset_timestamps 1`
            ])

            // 📁 SALIDA
            .output(path.join(config.CARPETA_TEMPORAL, `${titulo}_%03d.mp4`))
            .outputFormat('mp4');

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        comando.on('progress', (progreso) => {
            const por = progreso.percent || 0;
            if (por % 30 === 0) { // Mostrar poco para no frenar
                log.detalle(`⚡ ${por.toFixed(0)}%`);
            }
        });

        comando.on('end', () => {
            log.exito('✅ LISTO! Video generado en tiempo récord');
            resolve(true);
        });

        comando.on('error', (err) => {
            log.error('ERROR FFMPEG', err);
            reject(err);
        });

        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
