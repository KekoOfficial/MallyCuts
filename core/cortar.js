// ==============================================
// 💥 MODO DIOS - VELOCIDAD Y ESTABILIDAD TOTAL
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../routes/config');
const fs = require('fs').promises;
const chokidar = require('chokidar'); // 👈 Para detectar archivos en tiempo real

// ✅ IMPORTAR MÓDULOS
const { enviarVideo } = require('../routes/telegram');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

// ==============================================
// ⚙️ CONFIGURACIÓN DIOS
// ==============================================
const ESPERA_ENTRE_VIDEOS = 5000; // 5s
const INTENTOS_MAXIMOS = 3;

// ==============================================
// 🧠 FUNCIÓN: AJUSTE DE AUDIO INTELIGENTE
// ==============================================
function generarFiltroAudio(velocidad) {
    let filtros = [];
    let vel = velocidad;
    
    // Soporta velocidades mayores a 2x encadenando filtros
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
// 🔁 FUNCIÓN: ENVIAR CON REINTENTOS AUTOMÁTICOS
// ==============================================
async function enviarConRetry(ruta, titulo, parte, total) {
    for (let i = 0; i < INTENTOS_MAXIMOS; i++) {
        try {
            await enviarVideo(ruta, titulo, parte, total);
            return true;
        } catch (err) {
            if (i === INTENTOS_MAXIMOS - 1) throw err;
            log.warn(`⚠️ Falló envío. Reintento ${i+1}/${INTENTOS_MAXIMOS}...`);
            await dormir(3000);
        }
    }
}

// ==============================================
// 💤 FUNCIÓN DORMIR
// ==============================================
function dormir(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('💥 💀 MODO DIOS ACTIVADO');
        log.aviso('⚡ PARALELO TOTAL: CORTA + ENVÍA A LA VEZ');
        log.warn('🔥 Optimizado para archivos de HORAS');

        // 🧹 LIMPIAR NOMBRE
        const tituloArchivo = limpiarNombreParaArchivo(tituloOriginal);
        const rutaSalida = path.join(config.CARPETA_TEMPORAL, `${tituloArchivo}_%04d.mp4`);

        // ==============================================
        // 👁️ SISTEMA DE OBSERVACIÓN (WATCHER)
        // ==============================================
        // Detecta cuando aparece un archivo nuevo y lo envía INMEDIATAMENTE
        
        let archivosProcesados = [];
        let totalPartesEstimado = 0;

        const watcher = chokidar.watch(config.CARPETA_TEMPORAL, {
            persistent: true,
            ignoreInitial: true,
            depth: 0
        });

        watcher.on('add', async (filePath) => {
            // Solo tocar los nuestros
            if (!path.basename(filePath).startsWith(tituloArchivo)) return;

            // Esperar a que el archivo se escriba completamente
            await dormir(1000);

            try {
                // Extraer número de parte del nombre
                const match = filePath.match(/(\d+)\.mp4$/);
                const numeroParte = match ? parseInt(match[1]) : archivosProcesados.length + 1;
                
                log.info(`🚀 DETECTADO NUEVO: Parte ${numeroParte}`);

                // 📤 ENVIAR CON SEGURIDAD
                await enviarConRetry(filePath, tituloOriginal, numeroParte, '?');

                // 🗑️ BORRAR
                if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                    await fs.unlink(filePath);
                    log.dato(`🗑️ Limpio: ${path.basename(filePath)}`);
                }

                archivosProcesados.push(filePath);

                // ⏸️ PAUSA
                log.info(`⏸️ Esperando ${ESPERA_ENTRE_VIDEOS/1000}s...`);
                await dormir(ESPERA_ENTRE_VIDEOS);

            } catch (error) {
                log.error('💥 ERROR EN ENVÍO', error);
            }
        });

        // ==============================================
        // 🎬 COMANDO FFMPEG - MÁXIMA POTENCIA
        // ==============================================
        
        const comando = ffmpeg(rutaArchivo)
            
            // 🔧 POTENCIA BRUTA
            .nativeFramerate()
            .withOption('-threads', '0')
            .withOption('-nostdin')
            .withOption('-avioflags', 'direct')
            .withOption('-fflags', '+genpts') // Soluciona errores de tiempo
            .withOption('-avoid_negative_ts', 'make_zero')

            // 🎞️ FILTROS
            .videoFilters([
                `setpts=1/${config.VELOCIDAD_VIDEO}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(generarFiltroAudio(config.VELOCIDAD_VIDEO)) // 👈 Audio Dios

            // 📦 CODIFICACIÓN RÁPIDA
            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')
            .addOption('-crf', '32')
            .addOption('-tune', 'fastdecode')
            .addOption('-max_muxing_queue_size', '8192')
            .addOption('-movflags', '+faststart') // Mejora reproducción

            // 🎧 AUDIO
            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1)

            // ✂️ SEGMENTOS
            .outputOptions([
                `-f segment`,
                `-segment_time ${config.DURACION_POR_PARTE}`,
                `-reset_timestamps 1`
            ])

            .output(rutaSalida)
            .outputFormat('mp4');

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        let ultimoPorcentaje = 0;
        comando.on('progress', (progreso) => {
            const por = progreso.percent || 0;
            if (por >= ultimoPorcentaje + 10) {
                log.detalle(`⚡ Procesando: ${por.toFixed(0)}%`);
                ultimoPorcentaje = por;
            }
        });

        // ==============================================
        // ✅ FINALIZACIÓN
        // ==============================================
        comando.on('end', async () => {
            log.exito('✅ ✅ CORTE FINALIZADO COMPLETAMENTE');
            
            // Esperar a que terminen los últimos envíos
            await dormir(5000);
            
            // Cerrar el vigilante
            watcher.close();
            
            log.exito('🎉 🎥 MISION CUMPLIDA - TODO ENVIADO');
            resolve(true);
        });

        comando.on('error', (err) => {
            log.error('💥 ERROR FFMPEG', err);
            watcher.close();
            reject(err);
        });

        // 🚀 EJECUTAR
        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
