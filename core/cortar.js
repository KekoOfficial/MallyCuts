// 🎥 MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Se encarga de dividir el video en partes, aplicar velocidad y agregar la marca de agua

const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const config = require('../config');
const log = require('../js/logger');

/**
 * Extrae un segmento del video completo, le aplica los ajustes y guarda el archivo
 * @param {string} rutaVideoOriginal - Ruta completa del archivo de video que se va a procesar
 * @param {number} numeroParte - Número de la parte que se está generando
 * @param {string} tituloOriginal - Título del video para referencia
 * @returns {Promise<string|null>} Retorna la ruta del archivo generado si salió bien, o null si falló
 */
async function extraerSegmento(rutaVideoOriginal, numeroParte, tituloOriginal) {
    return new Promise(async (resolve, reject) => {
        try {
            // Calculamos el punto de inicio y la duración de esta parte
            const segundoInicio = (numeroParte - 1) * config.CLIP_DURATION;
            const duracionParte = config.CLIP_DURATION;

            // Definimos el nombre y ruta donde se va a guardar la parte generada
            const nombreArchivoSalida = `parte_${numeroParte}.mp4`;
            const rutaArchivoSalida = path.join(config.TEMP_FOLDER, nombreArchivoSalida);

            log.detalle(`Procesando parte ${numeroParte} | Inicio: ${segundoInicio}s | Duración: ${duracionParte}s`);

            // 👇 COMANDO CORREGIDO Y COMPLETO DE FFMPEG
            // Separamos filtros de video y filtros de audio para evitar errores
            const argumentosFFmpeg = [
                '-y', // Sobrescribir archivos sin preguntar
                '-ss', segundoInicio.toString(), // Punto de inicio del corte
                '-i', rutaVideoOriginal, // Archivo de video original
                '-t', duracionParte.toString(), // Duración de la parte

                // 🎥 FILTROS SOLO PARA VIDEO
                '-vf', `
                    setpts=(1/${config.VELOCIDAD_PREDETERMINADA})*PTS,
                    drawtext=
                        text='${config.TEXTO_MARCA_PREDETERMINADA}':
                        x=15:
                        y=15:
                        fontsize=22:
                        fontcolor=white@0.8:
                        fontfile=/system/fonts/Roboto-Regular.ttf:
                        box=1:
                        boxcolor=black@0.3:
                        boxborderw=3
                `.replace(/\s+/g, ' ').trim(), // Limpiamos espacios para que funcione bien

                // 🔊 FILTROS SOLO PARA AUDIO
                '-af', `atempo=${config.VELOCIDAD_PREDETERMINADA}`,

                // ⚙️ AJUSTES DE CALIDAD Y COMPATIBILIDAD
                '-c:v', 'libx264',       // Codificador de video
                '-c:a', 'aac',           // Codificador de audio
                '-b:v', '2M',            // Calidad de video (2 Mbps, podés subirlo si querés mejor calidad)
                '-b:a', '128k',          // Calidad de audio
                '-preset', 'fast',       // Velocidad de procesamiento
                '-crf', '23',            // Nivel de compresión (menor número = mayor calidad)
                '-pix_fmt', 'yuv420p',   // Formato compatible con todos los reproductores
                '-avoid_negative_ts', 'make_zero',
                '-movflags', '+faststart',
                '-hide_banner',          // Ocultar mensajes innecesarios de FFmpeg
                '-loglevel', 'error',    // Solo mostrar errores importantes
                rutaArchivoSalida         // Ruta final donde se guarda el archivo
            ];

            // Ejecutamos el comando de procesamiento
            execFile('ffmpeg', argumentosFFmpeg, (error, stdout, stderr) => {
                // Si hubo un error al ejecutar el comando
                if (error) {
                    log.error(`No se pudo generar la parte ${numeroParte}`, error);
                    return reject(null);
                }

                // Verificamos que el archivo se haya creado correctamente
                if (fs.existsSync(rutaArchivoSalida)) {
                    const tamañoArchivo = (fs.statSync(rutaArchivoSalida).size / (1024 * 1024)).toFixed(2);
                    log.exito(`Parte ${numeroParte} generada | Tamaño: ${tamañoArchivo} MB`);
                    resolve(rutaArchivoSalida);
                } else {
                    log.error(`El archivo de la parte ${numeroParte} no se creó`);
                    reject(null);
                }
            });

        } catch (errorGeneral) {
            log.error(`Error inesperado al procesar la parte ${numeroParte}`, errorGeneral);
            reject(null);
        }
    });
}

// Exportamos la función para usarla en el resto del sistema
module.exports = {
    extraerSegmento
};
