// ==============================================
// ⚡ MODO MISIL - VELOCIDAD MÁXIMA TERMUX
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs').promises;

// ✅ IMPORTAR MÓDULOS
const { enviarVideo } = require('../routes/telegram');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

// ==============================================
// ⏱️ TIEMPO DE ESPERA ENTRE VIDEOS (5 SEGUNDOS)
// ==============================================
const ESPERA_ENTRE_VIDEOS = 5000; // 5000 milisegundos = 5 segundos

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, tituloOriginal) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('⚡ MODO MISIL ACTIVADO');
        log.aviso('🔥 MODO: CORRER TODO PRIMERO | ENVIAR CON PAUSA');

        // 🧹 LIMPIAR NOMBRE PARA EL ARCHIVO
        const tituloArchivo = limpiarNombreParaArchivo(tituloOriginal);

        // ==============================================
        // 🎬 COMANDO FFMPEG ULTRA RÁPIDO
        // ==============================================
        
        const comando = ffmpeg(rutaArchivo)
            
            .nativeFramerate()
            .withOption('-threads', '0')
            .withOption('-nostdin')

            .videoFilters([
                `setpts=1/${config.VELOCIDAD_VIDEO}*PTS`,
                `scale=-2:720, format=yuv420p`
            ])
            .audioFilter(`atempo=${config.VELOCIDAD_VIDEO}`)

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
                `-segment_time ${config.DURACION_POR_PARTE}`,
                `-reset_timestamps 1`
            ])

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
        // ✅ CUANDO TERMINA DE CORTAR TODO
        // ==============================================
        comando.on('end', async () => {
            log.exito('✅ TODOS LOS VIDEOS CORTADOS');
            log.info('⏳ Preparando envío escalonado...');
            
            try {
                // 📂 BUSCAR ARCHIVOS GENERADOS
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                const partes = archivos.filter(arch => arch.startsWith(tituloArchivo)).sort(); // Ordenados

                if (partes.length === 0) throw new Error('No se encontraron archivos');

                const totalPartes = partes.length;
                log.inicio(`📤 Total a enviar: ${totalPartes} archivo(s)`);

                // ==============================================
                // 🔁 BUCLE DE ENVÍO CON PAUSA
                // ==============================================
                for (let i = 0; i < partes.length; i++) {
                    const parte = partes[i];
                    const rutaCompleta = path.join(config.CARPETA_TEMPORAL, parte);
                    const numeroParte = i + 1;
                    
                    log.info(`📤 Enviando: ${numeroParte}/${totalPartes}`);
                    
                    // 🚀 ENVIAR VIDEO
                    await enviarVideo(rutaCompleta, tituloOriginal, numeroParte, totalPartes);

                    // 🗑️ BORRAR SI ESTÁ CONFIGURADO
                    if(config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                        await fs.unlink(rutaCompleta);
                    }

                    // ⏸️ ESPERAR ANTES DE SIGUIENTE (SI NO ES EL ÚLTIMO)
                    if (i < partes.length - 1) {
                        log.info(`⏳ Esperando ${ESPERA_ENTRE_VIDEOS/1000}s...`);
                        await dormir(ESPERA_ENTRE_VIDEOS);
                    }
                }

                log.exito('✅ ✅ PROCESO FINALIZADO COMPLETO');
                resolve(true);

            } catch (error) {
                log.error('💥 ERROR', error);
                reject(error);
            }
        });

        comando.on('error', (err) => {
            log.error('💥 ERROR FFMPEG', err);
            reject(err);
        });

        comando.run();
    });
}

// ==============================================
// 💤 FUNCIÓN PARA DORMIR / ESPERAR
// ==============================================
function dormir(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { extraerYEditarSegmento };
