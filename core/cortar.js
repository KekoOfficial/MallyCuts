// ==============================================
// 💥 MODO DIOS 2.0 - ESTABLE + PARALELO REAL
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../routes/config');
const fs = require('fs').promises;
const chokidar = require('chokidar');

const { enviarVideo } = require('../routes/enviar');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

// ==============================================
// ⚙️ CONFIG
// ==============================================
const ESPERA_ENTRE_VIDEOS = 5000;
const MAX_REINTENTOS = 3;

// ==============================================
// 🧠 AUDIO INTELIGENTE
// ==============================================
function generarFiltroAudio(velocidad) {
    let filtros = [];
    let vel = velocidad;

    while (vel > 2.0) {
        filtros.push('atempo=2.0');
        vel /= 2;
    }
    while (vel < 0.5) {
        filtros.push('atempo=0.5');
        vel *= 2;
    }

    filtros.push(`atempo=${vel.toFixed(2)}`);
    return filtros.join(',');
}

// ==============================================
// 💤 SLEEP
// ==============================================
const dormir = ms => new Promise(r => setTimeout(r, ms));

// ==============================================
// 📦 ESPERAR ARCHIVO COMPLETO
// ==============================================
async function esperarArchivoCompleto(ruta) {
    let tamañoAnterior = -1;

    while (true) {
        const { size } = await fs.stat(ruta);

        if (size === tamañoAnterior) break;

        tamañoAnterior = size;
        await dormir(500);
    }
}

// ==============================================
// 🔁 RETRY ENVÍO
// ==============================================
async function enviarConRetry(ruta, titulo, parte, total) {
    for (let i = 1; i <= MAX_REINTENTOS; i++) {
        try {
            await enviarVideo(ruta, titulo, parte, total);
            return;
        } catch (err) {
            log.info(`⚠️ Reintento ${i}/${MAX_REINTENTOS}`);
            if (i === MAX_REINTENTOS) throw err;
            await dormir(2000);
        }
    }
}

// ==============================================
// 🔢 EXTRAER NÚMERO DE PARTE
// ==============================================
function obtenerNumeroParte(nombre) {
    const match = nombre.match(/_(\d+)\.mp4$/);
    return match ? parseInt(match[1]) : 0;
}

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================
async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {

    return new Promise((resolve, reject) => {

        log.separador();
        log.inicio('💀 MODO DIOS 2.0 ACTIVADO');
        log.aviso('⚡ COLA INTELIGENTE + STREAMING');

        const tituloArchivo = limpiarNombreParaArchivo(tituloOriginal);
        const rutaSalida = path.join(config.CARPETA_TEMPORAL, `${tituloArchivo}_%04d.mp4`);

        let procesando = true;

        // ==============================================
        // 📦 COLA DE ENVÍO
        // ==============================================
        const cola = [];
        let enviando = false;
        let partesEnviadas = 0;

        async function procesarCola() {
            if (enviando || cola.length === 0) return;

            enviando = true;
            const item = cola.shift();

            try {
                partesEnviadas++;

                log.info(`📤 Enviando parte ${item.parte}`);

                await enviarConRetry(item.ruta, tituloOriginal, item.parte, '?');

                if (config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                    await fs.unlink(item.ruta);
                }

                await dormir(ESPERA_ENTRE_VIDEOS);

            } catch (err) {
                log.error('💥 ERROR ENVÍO FINAL', err);
            }

            enviando = false;
            procesarCola();
        }

        // ==============================================
        // 👁️ WATCHER
        // ==============================================
        const watcher = chokidar.watch(config.CARPETA_TEMPORAL, {
            ignoreInitial: true
        });

        watcher.on('add', async (filePath) => {

            if (!path.basename(filePath).startsWith(tituloArchivo)) return;

            try {
                await esperarArchivoCompleto(filePath);

                const parte = obtenerNumeroParte(filePath);

                log.info(`📦 Parte lista: ${parte}`);

                cola.push({
                    ruta: filePath,
                    parte
                });

                // ordenar cola por número real
                cola.sort((a, b) => a.parte - b.parte);

                procesarCola();

            } catch (err) {
                log.error('💥 ERROR WATCHER', err);
            }
        });

        // ==============================================
        // 🎬 FFMPEG
        // ==============================================
        const comando = ffmpeg(rutaArchivo)

            .nativeFramerate()
            .withOption('-threads', '0')
            .withOption('-fflags', '+genpts')
            .withOption('-avoid_negative_ts', 'make_zero')

            .videoFilters([
                `setpts=1/${config.VELOCIDAD_VIDEO}*PTS`,
                `scale=-2:720,format=yuv420p`
            ])
            .audioFilter(generarFiltroAudio(config.VELOCIDAD_VIDEO))

            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')
            .addOption('-crf', '32')
            .addOption('-movflags', '+faststart')

            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1)

            .outputOptions([
                '-f segment',
                `-segment_time ${config.DURACION_POR_PARTE}`,
                '-reset_timestamps 1'
            ])

            .output(rutaSalida)
            .outputFormat('mp4');

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        comando.on('progress', p => {
            if (p.percent) {
                log.detalle(`⚡ ${p.percent.toFixed(0)}%`);
            }
        });

        // ==============================================
        // ✅ FIN
        // ==============================================
        comando.on('end', async () => {
            procesando = false;
            log.exito('✅ FFMPEG TERMINADO');

            // esperar a que cola termine
            while (cola.length > 0 || enviando) {
                await dormir(1000);
            }

            watcher.close();

            log.exito('🎉 TODO COMPLETADO');
            resolve(true);
        });

        // ==============================================
        // ❌ ERROR
        // ==============================================
        comando.on('error', err => {
            log.error('💥 FFMPEG ERROR', err);
            watcher.close();
            reject(err);
        });

        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
