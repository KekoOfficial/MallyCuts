// ✂️ MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Versión optimizada y adaptada a la configuración actual

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');

// Importamos módulos internos
const log = require('../js/logger');
const config = require('../config');

// Convertimos exec a promesa para poder usar async/await
const ejecutarComando = util.promisify(exec);

/**
 * Extrae un segmento específico del video original
 * @param {string} rutaOriginal - Ruta completa del archivo fuente
 * @param {number} numeroParte - Número de la parte a generar
 * @param {string} tituloVideo - Título para nombrar el archivo
 * @returns {Promise<string|null>} Ruta del archivo generado o null si falla
 */
async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo) {
    try {
        // Verificamos que el archivo original exista
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // Tomamos los parámetros de la configuración
        const duracionPorParte = config.DURACION_POR_PARTE || 60;
        const velocidad = config.VELOCIDAD_VIDEO || 1.0;

        // Calculamos el punto de inicio
        const tiempoInicio = (numeroParte - 1) * duracionPorParte;

        // Creamos el nombre y ruta de salida (usamos TEMP_FOLDER de tu config)
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_parte_${numeroParte}.mp4`;
        
        // ✅ IMPORTANTE: Usamos la variable correcta de tu configuración
        const rutaArchivoSalida = path.join(config.TEMP_FOLDER, nombreArchivoSalida);

        log.detalle(`Generando parte ${numeroParte}: desde el segundo ${tiempoInicio} por ${duracionPorParte} segundos`);
        log.detalle(`Archivo de salida: ${rutaArchivoSalida}`);

        // Comando FFmpeg optimizado
        // -ss inicio, -t duración
        // -filter:v y -filter:a para ajustar velocidad
        // -preset fast para rendimiento bueno en Termux
        const comando = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionPorParte} ` +
            `-filter:v "setpts=PTS/${velocidad}" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${rutaArchivoSalida}"`;

        // Ejecutamos el proceso
        const { stderr } = await ejecutarComando(comando);

        // Verificamos que el archivo se generó bien
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            return rutaArchivoSalida;
        } else {
            throw new Error('El archivo generado es demasiado pequeño o está vacío');
        }

    } catch (error) {
        log.error(`Error al generar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
