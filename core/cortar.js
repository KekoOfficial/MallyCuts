// ==============================================
// ⚡ MODO MISIL - VELOCIDAD MÁXIMA TERMUX
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs').promises;

// ✅ IMPORTAR MÓDULO DE TELEGRAM
const { enviarVideo } = require('../routes/telegram');

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, titulo) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('⚡ MODO MISIL ACTIVADO');
        log.aviso('🔥 VELOCIDAD EXTREMA | LISTO PARA SUBIR');

        // ==============================================
        // 🎬 COMANDO FFMPEG ULTRA RÁPIDO
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
            .output(path.join(config.CARPETA_TEMPORAL, `${titulo}_%03d.mp4`))
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
        // ✅ CUANDO TERMINA, ENVIAR A TELEGRAM
        // ==============================================
        
        comando.on('end', async () => {
            log.exito('✅ VIDEO CORTADO | LISTO PARA ENVIAR');
            
            try {
                // 📂 BUSCAR ARCHIVOS GENERADOS
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                const partes = archivos.filter(arch => arch.startsWith(titulo));

                if (partes.length === 0) {
                    throw new Error('No se encontraron partes para enviar');
                }

                log.inicio(`📤 ENCOLADOS: ${partes.length} archivo(s)`);

                // 🚀 ENVIAR CADA PARTE
                for (const parte of partes) {
                    const rutaCompleta = path.join(config.CARPETA_TEMPORAL, parte);
                    
                    log.info(`📤 Subiendo: ${parte}`);
                    
                    // 📤 ENVIAR A CANALES (Público y Privado)
                    await enviarVideo(rutaCompleta, titulo);

                    // 🗑️ BORRAR DESPUÉS DE ENVIAR (Si está activado en config)
                    if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                        await fs.unlink(rutaCompleta);
                        log.dato(`🗑️ Eliminado: ${parte}`);
                    }
                }

                log.exito('✅ ✅ PROCESO FINALIZADO COMPLETO');
                resolve(true);

            } catch (error) {
                log.error('💥 ERROR EN ETAPA FINAL', error);
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

        // 🚀 EJECUTAR
        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
