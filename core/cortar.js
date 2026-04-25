// ==============================================
// 💥 MODO DIOS 2.0 - VERSIÓN FINAL INDESTRUCTIBLE
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
    while (vel > 2.0) { filtros.push('atempo=2.0'); vel /= 2; }
    while (vel < 0.5) { filtros.push('atempo=0.5'); vel *= 2; }
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
    for(let i=0; i<10; i++){ // Intentar hasta 10 veces (5 seg)
        const stats = await fs.stat(ruta).catch(() => ({ size: -1 }));
        if (stats.size === tamañoAnterior && stats.size > 0) break;
        tamañoAnterior = stats.size;
        await dormir(500);
    }
}

// ==============================================
// 🔁 RETRY ENVÍO
// ==============================================
async function enviarConRetry(ruta, titulo, parte, total) {
    for (let i = 1; i <= MAX_REINTENTOS; i++) {
        try {
            await fs.access(ruta);
            await enviarVideo(ruta, titulo, parte, total);
            return true;
        } catch (err) {
            log.info(`⚠️ Reintento ${i}/${MAX_REINTENTOS} fallido`);
            if (i === MAX_REINTENTOS) throw err;
            await dormir(3000);
        }
    }
}

// ==============================================
// 🔢 EXTRAER NÚMERO DE PARTE
// ==============================================
function obtenerNumeroParte(nombreArchivo) {
    const match = nombreArchivo.match(/_(\d+)\.mp4$/);
    return match ? parseInt(match[1], 10) : 9999;
}

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================
async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {
    return new Promise(async (resolve, reject) => {

        log.separador();
        log.inicio('💀 MODO DIOS 2.0 ACTIVADO');
        log.info('⚡ COLA INTELIGENTE + STREAMING');

        const tituloArchivo = limpiarNombreParaArchivo(tituloOriginal);
        const rutaSalida = path.join(config.CARPETA_TEMPORAL, `${tituloArchivo}_%04d.mp4`);

        let procesando = true;
        let archivosGenerados = [];

        // ==============================================
        // 📦 COLA DE ENVÍO
        // ==============================================
        const cola = [];
        let enviando = false;

        async function procesarCola() {
            if (enviando || cola.length === 0) return;
            enviando = true;
            const item = cola.shift();

            try {
                log.info(`📤 Enviando parte ${item.parte}`);
                await enviarConRetry(item.ruta, tituloOriginal, item.parte, '?');
                
                if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                    await fs.unlink(item.ruta).catch(()=>{});
                }
                
                await dormir(ESPERA_ENTRE_VIDEOS);
            } catch (err) {
                log.error('💥 ERROR ENVÍO', err);
            }

            enviando = false;
            procesarCola();
        }

        // ==============================================
        // 👁️ WATCHER
        // ==============================================
        const watcher = chokidar.watch(config.CARPETA_TEMPORAL, {
            ignoreInitial: true,
            depth: 0,
            interval: 500, // Revisar cada medio segundo
        });

        watcher.on('add', async (filePath) => {
            const nombreArchivo = path.basename(filePath);
            
            if (!nombreArchivo.startsWith(tituloArchivo)) return;
            if (!nombreArchivo.endsWith('.mp4')) return;
            if (nombreArchivo.includes('%')) return;

            try {
                await dormir(1000); // Esperar un poquito más
                await esperarArchivoCompleto(filePath);

                const parte = obtenerNumeroParte(nombreArchivo);
                archivosGenerados.push(filePath);

                log.info(`📦 Parte lista: ${parte}`);

                cola.push({ ruta: filePath, parte });
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
            .withOption('-threads', '2')
            .withOption('-nostdin')
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
            .addOption('-max_muxing_queue_size', '1024')

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

        comando.on('progress', p => {
            if (p.percent) log.detalle(`⚡ ${p.percent.toFixed(0)}%`);
        });

        // ==============================================
        // ✅ FINALIZACIÓN CON SISTEMA DE RESCATE
        // ==============================================
        comando.on('end', async () => {
            procesando = false;
            log.exito('✅ FFMPEG TERMINADO');

            // 🦸‍♂️ SISTEMA DE RESCATE: Si el watcher no detectó alguno, lo buscamos nosotros
            await dormir(3000);
            try {
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                for(const archivo of archivos){
                    if(archivo.startsWith(tituloArchivo) && archivo.endsWith('.mp4') && !archivo.includes('%')){
                        const rutaCompleta = path.join(config.CARPETA_TEMPORAL, archivo);
                        
                        if(!archivosGenerados.includes(rutaCompleta)){
                            log.info(`🦸 RESCATE: Encontrado ${archivo}`);
                            const parte = obtenerNumeroParte(archivo);
                            cola.push({ ruta: rutaCompleta, parte });
                            cola.sort((a, b) => a.parte - b.parte);
                        }
                    }
                }
                procesarCola();
            } catch(e){}

            // Esperar a que todo termine
            while (cola.length > 0 || enviando) {
                await dormir(1000);
            }

            watcher.close();
            log.exito('🎉 TODO COMPLETADO');
            resolve(true);
        });

        comando.on('error', (err) => {
            log.error('💥 FFMPEG ERROR', err.message);
            watcher.close();
            reject(err);
        });

        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
