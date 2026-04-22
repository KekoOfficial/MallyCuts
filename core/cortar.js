const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');

/**
 * Extrae un segmento de vídeo, optimizado para archivos de cualquier duración
 * @param {string} rutaEntrada - Ruta del vídeo original
 * @param {number} numeroParte - Número de la parte que se va a cortar
 * @returns {Promise<string|null>} Ruta del archivo generado o null si falló
 */
function extraerSegmento(rutaEntrada, numeroParte) {
    return new Promise((resolve) => {
        // Calculamos el segundo exacto donde empieza el corte
        const inicio = (numeroParte - 1) * config.CLIP_DURATION;
        const rutaSalida = path.join(config.TEMP_FOLDER, `parte_${numeroParte}.mp4`);

        // Comando OPTIMIZADO para vídeos largos
        // Usamos -ss ANTES de -i para que busque la posición mucho más rápido
        const comando = [
            '-y',                          // Sobrescribe archivos si ya existen
            '-ss', inicio.toString(),      // ⚡ Buscamos la posición de inicio rápido
            '-i', rutaEntrada,             // Archivo de entrada
            '-t', config.CLIP_DURATION.toString(), // Duración exacta del segmento
            '-c', 'copy',                  // Copia directa sin recodificar (máxima velocidad)
            '-avoid_negative_ts', 'make_zero', // Arregla problemas de sincronización
            '-fflags', '+genpts',          // ⚡ Parámetro clave para vídeos muy largos
            '-async', '1',                 // Corrige desincronización de audio/vídeo
            '-movflags', '+faststart',     // Hace que el archivo se pueda reproducir rápido
            rutaSalida
        ];

        // Ejecutamos el comando con buffer grande para archivos pesados
        execFile('ffmpeg', comando, {
            maxBuffer: 1024 * 1024 * 200, // Buffer de 200MB para que no se corte por falta de memoria
            timeout: 60000 // Tiempo máximo de espera por corte (1 minuto)
        }, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ Error al cortar parte ${numeroParte}:`, error.message);
                console.error(`📝 Detalles técnicos:`, stderr);
                return resolve(null);
            }

            // Verificamos que el archivo se haya creado correctamente
            if (fs.existsSync(rutaSalida)) {
                // Verificamos que el archivo tenga tamaño mayor a 0 (no esté vacío)
                const stats = fs.statSync(rutaSalida);
                if (stats.size > 1000) { // Si pesa más de 1KB, está bien
                    console.log(`✅ Parte ${numeroParte} cortada correctamente`);
                    resolve(rutaSalida);
                } else {
                    console.error(`⚠️ Parte ${numeroParte} se generó vacía`);
                    fs.unlinkSync(rutaSalida); // Eliminamos el archivo malo
                    resolve(null);
                }
            } else {
                console.error(`❌ No se generó el archivo de la parte ${numeroParte}`);
                resolve(null);
            }
        });
    });
}

module.exports = { extraerSegmento };
