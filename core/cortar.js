// ==============================================
// ⚡ MODO MISIL - VELOCIDAD MÁXIMA TERMUX
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs').promises;

// ✅ IMPORTAR FUNCIÓN DE TELEGRAM
const { enviarVideo } = require('../routes/telegram'); // Ajusta la ruta si es diferente

const PARAMETROS = {
    DURACION_PARTE: 120,
    VELOCIDAD: 1.30
};

async function extraerYEditarSegmento(rutaArchivo, titulo) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('⚡ MODO MISIL ACTIVADO');
        log.aviso('🔥 VELOCIDAD EXTREMA | LISTO PARA ENVIAR');

        const comando = ffmpeg(rutaArchivo)
            .nativeFramerate()
            .withOption('-threads', '0')
            .withOption('-nostdin')

            .videoFilters([
                `setpts=1/${PARAMETROS.VELOCIDAD}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(`atempo=${PARAMETROS.VELOCIDAD}`)

            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')
            .addOption('-crf', '30')
            .addOption('-tune', 'fastdecode')
            .addOption('-max_muxing_queue_size', '1024')

            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1)

            .outputOptions([
                `-f segment`,
                `-segment_time ${PARAMETROS.DURACION_PARTE}`,
                `-reset_timestamps 1`
            ])

            .output(path.join(config.CARPETA_TEMPORAL, `${titulo}_%03d.mp4`))
            .outputFormat('mp4');

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        comando.on('progress', (progreso) => {
            const por = progreso.percent || 0;
            if (por % 30 === 0) {
                log.detalle(`⚡ ${por.toFixed(0)}%`);
            }
        });

        // ==============================================
        // ✅ CUANDO TERMINA, ENVIAR A TELEGRAM
        // ==============================================
        comando.on('end', async () => {
            log.exito('✅ VIDEO LISTO');
            log.inicio('📤 INICIANDO ENVÍO A TELEGRAM...');

            try {
                // Buscar los archivos generados
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                const partes = archivos.filter(archivo => archivo.startsWith(titulo));

                if(partes.length === 0) {
                    throw new Error('No se encontraron partes para enviar');
                }

                // Enviar cada parte
                for(const parte of partes) {
                    const rutaParte = path.join(config.CARPETA_TEMPORAL, parte);
                    log.info(`📤 Enviando: ${parte}`);
                    
                    // 🚀 LLAMAR A TU FUNCIÓN
                    await enviarVideo(rutaParte, titulo);
                    
                    // (Opcional) Borrar después de enviar
                    await fs.unlink(rutaParte);
                }

                log.exito('✅ TODO ENVIADO EXITOSAMENTE');
                resolve(true);

            } catch (err) {
                log.error('❌ FALLO EN ENVÍO', err);
                reject(err);
            }
        });

        comando.on('error', (err) => {
            log.error('ERROR FFMPEG', err);
            reject(err);
        });

        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
