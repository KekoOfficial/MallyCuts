// ==============================================
// ⚡ MOTOR DE CORTE ULTRA RÁPIDO - MALLYCUTS
// ==============================================

const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../config');

// ==============================================
// ⚙️ CONFIGURACIÓN DE RENDIMIENTO
// ==============================================

const PARAMETROS = {
    DURACION_PARTE: 120, // Segundos (2 minutos)
    VELOCIDAD: 1.25,     // Velocidad de reproducción
    CALIDAD: '720p',     // Resolución objetivo
    CPU_USED: 4,         // Nivel de compresión (0=rápido, 8=máximo)
    THREADS: '0'         // 0 = Usar TODOS los núcleos disponibles
};

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL
// ==============================================

async function extraerYEditarSegmento(rutaArchivo, titulo) {
    
    return new Promise((resolve, reject) => {
        
        log.separador();
        log.inicio('🎬 INICIANDO PROCESAMIENTO AVANZADO');
        log.dato(`⚡ Velocidad: ${PARAMETROS.VELOCIDAD}x | Parte: ${PARAMETROS.DURACION_PARTE}s`);
        log.dato(`🔥 Modo: MÁXIMO RENDIMIENTO CPU`);

        // ==============================================
        // 🎥 COMANDO FFMPEG ULTRA OPTIMIZADO
        // ==============================================
        
        const comando = ffmpeg(rutaArchivo)
            
            // 🔧 OPCIONES GLOBALES
            .nativeFramerate()
            .withOption('-threads', PARAMETROS.THREADS)
            .withOption('-hwaccel', 'auto') // Aceleración hardware si existe

            // 🎞️ FILTROS COMPLEJOS (HACEMOS TODO EN UN SOLO PASO)
            .videoFilters([
                `setpts=1/${PARAMETROS.VELOCIDAD}*PTS`,      // Aumentar velocidad video
                `scale=-2:720, format=yuv420p`               // Redimensionar y optimizar color
            ])
            .audioFilter(`atempo=${PARAMETROS.VELOCIDAD}`)   // Aumentar velocidad audio

            // 📦 CÓDEC Y CALIDAD
            .videoCodec('libx264')
            .addOption('-preset', 'veryfast')      // Codificación rápida
            .addOption('-crf', '23')               // Calidad balanceada
            .addOption('-tune', 'zerolatency')     // Optimizar para velocidad
            .addOption('-cpu-used', PARAMETROS.CPU_USED)
            .addOption('-profile:v', 'main')       // Compatibilidad

            // 🎧 AUDIO
            .audioCodec('aac')
            .audioBitrate('128k')
            .audioChannels(2)

            // ✂️ DIVIDIR EN PARTES
            .outputOptions([
                `-f segment`,
                `-segment_time ${PARAMETROS.DURACION_PARTE}`,
                `-reset_timestamps 1`
            ])

            // 📁 SALIDA
            .output(path.join(config.CARPETA_TEMPORAL, `${titulo}_%03d.mp4`))
            .outputFormat('mp4');

        // ==============================================
        // 📢 EVENTOS
        // ==============================================
        
        let ultimoPorcentaje = 0;
        
        comando.on('progress', (progreso) => {
            const porcentaje = progreso.percent || 0;
            
            // Mostrar solo cada 10% para no llenar logs
            if (porcentaje >= ultimoPorcentaje + 10) {
                log.detalle(`⚡ Progreso: ${porcentaje.toFixed(0)}% | Tamaño: ${progreso.targetSize}kb`);
                ultimoPorcentaje = porcentaje;
            }
        });

        comando.on('end', () => {
            log.exito('✅ TODAS LAS PARTES GENERADAS');
            log.exito('⚡ Proceso finalizado a máxima velocidad');
            log.separador();
            resolve(true);
        });

        comando.on('error', (err) => {
            log.error('💥 ERROR FATAL EN FFMPEG', err);
            reject(err);
        });

        // 🚀 LANZAR
        comando.run();
    });
}

module.exports = { extraerYEditarSegmento };
