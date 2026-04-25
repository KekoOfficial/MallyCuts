// ==============================================
// ⚡ MÓDULO DE CORTE Y ENVÍO - MALLYCUTS
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs').promises;

// ✅ IMPORTAR MÓDULOS
const { enviarVideo } = require('./telegram');
const { limpiarNombreParaArchivo } = require('./titulo');

// ==============================================
// ⏱️ CONFIGURACIÓN DE TIEMPOS
// ==============================================
const ESPERA_ENTRE_VIDEOS = 5000; // 5 SEGUNDOS ENTRE CADA UNO

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('⚡ MODO MISIL ACTIVADO');
        log.aviso('🔥 MODO: CORRER TODO PRIMERO | ENVIAR CON PAUSA');

        // 🧹 LIMPIAR NOMBRE PARA EL ARCHIVO (sin caracteres raros)
        const tituloArchivo = limpiarNombreParaArchivo(tituloOriginal);

        // ==============================================
        // 🎬 COMANDO FFMPEG - CORTE TOTAL PRIMERO
        // ==============================================
        
        const comando = ffmpeg(rutaArchivo)
            
            // 🔧 OPCIONES DE RENDIMIENTO
            .nativeFramerate()
            .withOption('-threads', '0')       // Usar TODOS los núcleos
            .withOption('-nostdin')            // No esperar datos

            // 🎞️ FILTROS (Velocidad + Tamaño)
            .videoFilters([
                `setpts=1/${config.VELOCIDAD_VIDEO}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(`atempo=${config.VELOCIDAD_VIDEO}`)

            // 📦 CONFIGURACIÓN DE SALIDA RÁPIDA
            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')    // 🏎️ MÁS RÁPIDO POSIBLE
            .addOption('-crf', '30')             // Compresión equilibrada
            .addOption('-tune', 'fastdecode')    // Optimizar lectura
            .addOption('-max_muxing_queue_size', '1024')

            // 🎧 AUDIO LIGERO
            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1) // Mono = Más rápido

            // ✂️ DIVISIÓN EN PARTES
            .outputOptions([
                `-f segment`,
                `-segment_time ${config.DURACION_POR_PARTE}`,
                `-reset_timestamps 1`
            ])

            // 📁 RUTA DE SALIDA
            .output(path.join(config.CARPETA_TEMPORAL, `${tituloArchivo}_%03d.mp4`))
            .outputFormat('mp4');

        // ==============================================
        // 📊 PROGRESO
        // ==============================================
        
        let ultimoPorcentaje = 0;
        
        comando.on('progress', (progreso) => {
            const por = progreso.percent || 0;
            if (por >= ultimoPorcentaje + 10) {
                log.detalle(`⚡ Progreso: ${por.toFixed(0)}%`);
                ultimoPorcentaje = por;
            }
        });

        // ==============================================
        // ✅ CUANDO TERMINA DE CORTAR TODO...
        // ==============================================
        
        comando.on('end', async () => {
            log.exito('✅ ✅ TODOS LOS VIDEOS CORTADOS COMPLETAMENTE');
            log.info('⏳ INICIANDO SECUENCIA DE ENVÍO...');
            
            try {
                // 📂 BUSCAR ARCHIVOS GENERADOS Y ORDENARLOS
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                const partes = archivos
                    .filter(arch => arch.startsWith(tituloArchivo))
                    .sort(); // Asegura que vayan en orden 001, 002, 003...

                if (partes.length === 0) {
                    throw new Error('No se encontraron archivos para enviar');
                }

                const totalPartes = partes.length;
                log.inicio(`📤 Total a enviar: ${totalPartes} archivo(s)`);

                // ==============================================
                // 🔁 BUCLE: ENVIAR UNO -> ESPERAR 5s -> ENVIAR OTRO
                // ==============================================
                
                for (let i = 0; i < partes.length; i++) {
                    const parte = partes[i];
                    const rutaCompleta = path.join(config.CARPETA_TEMPORAL, parte);
                    const numeroParte = i + 1;
                    
                    log.info(`📤 Enviando: ${numeroParte}/${totalPartes} ⏳`);
                    
                    // 🚀 ENVIAR VIDEO A TELEGRAM
                    await enviarVideo(rutaCompleta, tituloOriginal, numeroParte, totalPartes);

                    // 🗑️ BORRAR DESPUÉS DE ENVIAR (Si está activado en config)
                    if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                        await fs.unlink(rutaCompleta);
                        log.dato(`🗑️ Eliminado: ${parte}`);
                    }

                    // ⏸️ PAUSA DE 5 SEGUNDOS (si no es el último)
                    if (i < partes.length - 1) {
                        log.info(`⏸️ ESPERANDO ${ESPERA_ENTRE_VIDEOS/1000} SEGUNDOS...`);
                        await dormir(ESPERA_ENTRE_VIDEOS);
                    }
                }

                // ==============================================
                // ✅ FINAL
                // ==============================================
                
                log.exito('🎉 🎥 PROCESO FINALIZADO AL 100%');
                log.exito('✅ Todos los videos enviados correctamente');
                resolve(true);

            } catch (error) {
                log.error('💥 ERROR EN EL PROCESO', error);
                reject(error);
            }
        });

        // ==============================================
        // ❌ MANEJO DE ERRORES
        // ==============================================
        
        comando.on('error', (err) => {
            log.error('💥 ERROR FFMPEG', err);
            reject(err);
        });

        // 🚀 EJECUTAR CORTE
        comando.run();
    });
}

// ==============================================
// 💤 FUNCIÓN PARA DORMIR / ESPERAR
// ==============================================
function dormir(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ==============================================
// 📦 EXPORTAR
// ==============================================
module.exports = { extraerYEditarSegmento };
