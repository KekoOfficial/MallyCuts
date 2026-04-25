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

// Función para crear el filtro de audio inteligente
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

        // Preparar nombres y rutas
        const tituloLimpio = limpiarNombreParaArchivo(tituloOriginal);
        const rutaSalida = path.join(config.CARPETA_TEMPORAL, tituloLimpio + '_%04d.mp4');

        // ==============================================
        // 🎬 COMANDO FFMPEG COMPLETO Y DETALLADO
        // ==============================================
        const comando = ffmpeg(rutaArchivo)

            // Opciones de rendimiento y estabilidad
            .nativeFramerate()
            .withOption('-threads', '2')
            .withOption('-nostdin')
            .withOption('-y') // Sobrescribir si existe
            .withOption('-fflags', '+genpts')
            .withOption('-avoid_negative_ts', 'make_zero')

            // Filtros de video y audio
            .videoFilters([
                `setpts=1/${config.VELOCIDAD}*PTS`,
                'scale=-2:720',
                'format=yuv420p'
            ])
            .audioFilters(generarFiltroAudio(config.VELOCIDAD))

            // Codecs y calidad
            .videoCodec('libx264')
            .addOption('-preset', 'ultrafast')
            .addOption('-crf', '32')
            .addOption('-movflags', '+faststart')

            .audioCodec('aac')
            .audioBitrate('96k')
            .audioChannels(1)

            // Configuración de segmentos
            .outputOptions([
                '-f segment',
                `-segment_time ${config.DURACION_POR_PARTE || 120}`,
                '-reset_timestamps 1'
            ])

            // Archivo de salida
            .output(rutaSalida)
            .outputFormat('mp4');

        // ==============================================
        // 📊 MOSTRAR PROGRESO
        // ==============================================
        comando.on('progress', progreso => {
            if (progreso.percent) {
                log.detalle(`⚡ ${progreso.percent.toFixed(0)}%`);
            }
        });

        // ==============================================
        // ✅ CUANDO TERMINA DE CORTAR
        // ==============================================
        comando.on('end', async () => {
            log.exito('✅ FFMPEG TERMINADO');
            log.info('📂 Iniciando envíos...');

            try {
                // Leer y ordenar archivos
                const archivos = await fs.readdir(config.CARPETA_TEMPORAL);
                let partes = archivos.filter(arch => 
                    arch.startsWith(tituloLimpio) && arch.endsWith('.mp4')
                );

                // Ordenar por número de parte
                partes.sort((a, b) => {
                    const numA = parseInt(a.match(/_(\d+)\.mp4$/)[1]);
                    const numB = parseInt(b.match(/_(\d+)\.mp4$/)[1]);
                    return numA - numB;
                });

                const totalPartes = partes.length;

                // ==============================================
                // 📤 ENVIAR UNO POR UNO
                // ==============================================
                for (let i = 0; i < partes.length; i++) {
                    const rutaCompleta = path.join(config.CARPETA_TEMPORAL, partes[i]);
                    const numeroParte = i + 1;

                    log.info(`📤 Enviando parte ${numeroParte} de ${totalPartes}`);
                    
                    // Enviar con seguridad
                    await enviarVideo(rutaCompleta, tituloOriginal, numeroParte, totalPartes);

                    // Borrar después de enviar
                    if (config.ELIMINAR_ARCHIVOS_AL_TERMINAR) {
                        await fs.unlink(rutaCompleta);
                    }

                    // Esperar entre envíos
                    await dormir(5000);
                }

                log.exito('🎉 TODO COMPLETADO CON ÉXITO');
                resolve(true);

            } catch (error) {
                log.error('💥 ERROR EN ETAPA FINAL', error);
                reject(error);
            }
        });

        // ==============================================
        // ❌ MANEJO DE ERRORES
        // ==============================================
        comando.on('error', (err, stdout, stderr) => {
            log.error('💥 ERROR FFMPEG', err.message);
            reject(err);
        });

        // Ejecutar
        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
