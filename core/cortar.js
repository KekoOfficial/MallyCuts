// ✂️ MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Divide el video en partes, ajusta velocidad y genera archivos finales

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');
const log = require('../js/logger');
const config = require('../config');

// Convertimos exec a promesa para usar async/await
const ejecutarComando = util.promisify(exec);

/**
 * Extrae un segmento del video original y lo procesa
 * @param {string} rutaOriginal - Ruta completa del archivo original
 * @param {number} numeroParte - Número de la parte que se va a generar
 * @param {string} tituloVideo - Título del video para nombrar los archivos
 * @param {number} duracionParte - Duración en segundos que tendrá cada parte
 * @param {number} velocidad - Velocidad de reproducción configurada
 * @returns {Promise<string|null>} Ruta del archivo generado o null si hubo error
 */
async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo, duracionParte, velocidad) {
    try {
        // Verificamos que el archivo original exista
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // Calculamos el tiempo de inicio del segmento
        const tiempoInicio = (numeroParte - 1) * duracionParte;

        // Creamos el nombre y ruta para el archivo resultante
        const nombreArchivoSalida = `${tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ')}_parte_${numeroParte}.mp4`;
        const rutaArchivoSalida = path.join(config.TEMP_FOLDER || config.TMP_FOLDER || config.TEMPORAL_FOLDER || config.TEMP_FOLDER, nombreArchivoSalida);

        log.detalle(`Generando parte ${numeroParte}: desde el segundo ${tiempoInicio} por ${duracionParte} segundos`);
        log.detalle(`Archivo de salida: ${rutaArchivoSalida}`);

        // Comando FFmpeg para cortar y ajustar velocidad
        // - Corte: -ss = tiempo inicio, -t = duración
        // - Velocidad: atempo para audio, setpts para video
        const comandoFFmpeg = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionParte} ` +
            `-filter:v "setpts=PTS/${velocidad}" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 192k "${rutaArchivoSalida}"`;

        // Ejecutamos el comando
        const { stdout, stderr } = await ejecutarComando(comandoFFmpeg);

        // Verificamos que el archivo generado sea válido
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            log.detalle(`Parte ${numeroParte} generada correctamente`);
            return rutaArchivoSalida;
        } else {
            throw new Error(`El archivo generado está vacío o dañado`);
        }

    } catch (error) {
        log.error(`Error al generar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
