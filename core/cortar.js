// ==============================================
// 💥 MODO DIOS - VERSIÓN COMPLETA Y ESTABLE
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../routes/config');
const fs = require('fs').promises;

const { enviarVideo } = require('../routes/enviar');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

// ==============================================
// ⚙️ FUNCIONES AUXILIARES
// ==============================================
const dormir = ms => new Promise(resolve => setTimeout(resolve, ms));

function generarFiltroAudio(velocidad) {
    let filtros = [];
    let vel = parseFloat(velocidad);

    while (vel > 2.0) {
        filtros.push('atempo=2.0');
        vel /= 2;
    }
    while (vel < 0.5) {
        filtros.push('atempo=0.5');
        vel *= 2;
    }
    filtros.push(`atempo=${vel.toFixed(2)}`);
    return filtros;
}

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================
async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {
    return new Promise(async (resolve, reject) => {

        log.separador();
        log.inicio('💀 MODO DIOS ACTIVADO');
        log.info('⚡ PROCESO SEGURO INICIADO');

        const tituloLimpio = limpiarNombreParaArchivo(tituloOriginal);
        const rutaSalida = path.join(config.CARPETA_TEMPORAL, tituloLimpio + '_%04d.mp4');

        // ==============================================
        // 🎬 FFMPEG
        // ==============================================
        const comando = ffmpeg(rutaArchivo)
            .nativeFramerate()
            .withOption('-threads', '2')
            .withOption('-nostdin')
            .withOption('-y')
            .withOption('-fflags', '+genpts')
            .withOption('-avoid_negative_ts', 'make_zero')

            .videoFilters([
                `setpts=1/${config.VELOCIDAD}*PTS`,
                'scale=-2:720',
                'format=yuv420p'
            ])
            .audioFilters(generarFiltroAudio(config.VELOCIDAD))

            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')
            .addOption('-crf', '32')
            .addOption('-movflags', '+faststart')

            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1)

            .outputOptions([
                '-f segment',
                `-segment_time ${config.DURACION_POR_PARTE || 120}`,
                '-reset_timestamps 1'
            ])
            .output(rutaSalida);

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        comando.on('progress', p => {
            if (p.percent) log.detalle(`⚡ ${p.percent.toFixed(0)}%`);
        });

        // ==============================================
        // ✅ FIN
        // ==============================================
        comando.on('end', async () => {
            log.exito('✅ FFMPEG TERMINADO');
            try {
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                let partes = archivos.filter(f => f.startsWith(tituloLimpio));
                partes.sort((a, b) => {
                    const na = parseInt(a.match(/_(\d+)\.mp4$/)[1]);
                    const nb = parseInt(b.match(/_(\d+)\.mp4$/)[1]);
                    return na - nb;
                });

                for(let i=0; i<partes.length; i++){
                    const r = path.join(config.CARPETA_TEMPORAL, partes[i]);
                    await enviarVideo(r, tituloOriginal, i+1, partes.length);
                    if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) await fs.unlink(r);
                    await dormir(5000);
                }
                resolve(true);
            } catch (e) { reject(e) }
        });

        comando.on('error', reject);
        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
