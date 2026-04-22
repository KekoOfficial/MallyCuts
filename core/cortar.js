const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');

/**
 * Corta el vídeo original en segmentos individuales
 * @param {string} rutaEntrada - Ruta completa del archivo de vídeo original
 * @param {number} numeroParte - Número de la parte que se va a generar
 * @returns {Promise<string|null>} Devuelve la ruta del archivo generado si todo salió bien, o null si hubo error
 */
function extraerSegmento(rutaEntrada, numeroParte) {
    return new Promise((resolve) => {
        // Calculamos el punto de inicio del corte
        const tiempoInicio = (numeroParte - 1) * config.CLIP_DURATION;
        // Definimos dónde se guardará la parte generada
        const rutaSalida = path.join(config.TEMP_FOLDER, `parte_${numeroParte}.mp4`);

        // 🚀 Comando FFmpeg OPTIMIZADO: más rápido, estable y compatible
        const comandoFFmpeg = [
            '-y',                          // Sobrescribe el archivo si ya existe
            '-ss', tiempoInicio.toString(),// Tiempo donde empieza el corte
            '-i', rutaEntrada,             // Archivo original de entrada
            '-t', config.CLIP_DURATION.toString(), // Duración exacta de la parte
            '-c:v', 'copy',                // Copia el vídeo sin volver a comprimir (más rápido)
            '-c:a', 'copy',                // Copia el audio sin volver a comprimir
            '-vf', 'format=yuv420p',       // Formato compatible con todos los reproductores y Telegram
            '-avoid_negative_ts', 'make_zero', // Corrige problemas de sincronización
            '-fflags', '+genpts+igndts',   // Mejora la lectura de tiempos y evita errores
            '-async', '1',                 // Sincroniza audio y vídeo
            '-movflags', '+faststart',     // Permite que el archivo se reproduzca mientras se descarga
            '-hide_banner',                // Oculta mensajes innecesarios en la consola
            '-loglevel', 'error',          // Solo muestra mensajes de error importantes
            rutaSalida
        ];

        // Ejecutamos el proceso de corte
        execFile('ffmpeg', comandoFFmpeg, {
            maxBuffer: 200 * 1024 * 1024, // Permite procesar archivos grandes sin errores de memoria
            timeout: 180000               // Tiempo máximo de espera por parte (3 minutos)
        }, (error, stdout, stderr) => {
            // Si hubo error al cortar
            if (error) {
                console.error(`❌ Error al generar la parte ${numeroParte}: ${error.message}`);
                if (stderr) console.error(`📝 Detalle del error: ${stderr}`);
                return resolve(null);
            }

            // ✅ Verificamos que el archivo se haya creado correctamente
            if (fs.existsSync(rutaSalida)) {
                const datosArchivo = fs.statSync(rutaSalida);
                const tamañoArchivoMB = (datosArchivo.size / 1024 / 1024).toFixed(2);

                // Comprobamos que el archivo no esté vacío ni dañado
                if (datosArchivo.size > 50 * 1024) { // Mínimo 50KB para ser considerado válido
                    console.log(`✅ Parte ${numeroParte} lista | Tamaño: ${tamañoArchivoMB} MB`);
                    resolve(rutaSalida);
                } else {
                    console.error(`⚠️ Parte ${numeroParte} se generó vacía o dañada | Tamaño: ${tamañoArchivoMB} MB`);
                    // Eliminamos el archivo que no sirve
                    if (fs.existsSync(rutaSalida)) fs.unlinkSync(rutaSalida);
                    resolve(null);
                }
            } else {
                console.error(`❌ No se pudo crear el archivo de la parte ${numeroParte}`);
                resolve(null);
            }
        });
    });
}

module.exports = { extraerSegmento };
