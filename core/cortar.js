// ✂️ MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Adaptado para la nueva estructura de configuración

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');

// Importamos módulos
const log = require('../js/logger');
const config = require('../config');

// Convertimos exec a promesa
const ejecutarComando = util.promisify(exec);

/**
 * Extrae un segmento del video original
 * @param {string} rutaOriginal - Ruta del archivo fuente
 * @param {number} numeroParte - Número de parte
 * @param {string} tituloVideo - Título para el nombre del archivo
 * @returns {Promise<string|null>} Ruta del archivo generado
 */
async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo) {
    try {
        // Verificar archivo original
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // ==============================================
        // TOMAMOS LOS DATOS DIRECTO DE TU CONFIG
        // ==============================================
        const carpetaSalida = config.CARPETA_TEMPORAL;
        const duracionPorParte = config.DURACION_POR_PARTE;
        const velocidad = config.VELOCIDAD_VIDEO;

        // Seguridad por si faltara algo
        if (!carpetaSalida || typeof carpetaSalida !== 'string') {
            throw new Error("La ruta CARPETA_TEMPORAL no está definida correctamente en config.js");
        }

        // Calculamos punto de inicio
        const tiempoInicio = (numeroParte - 1) * duracionPorParte;

        // Generamos nombre y ruta completa
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_parte_${numeroParte}.mp4`;
        const rutaArchivoSalida = path.join(carpetaSalida, nombreArchivoSalida);

        // Logs informativos
        log.detalle(`Generando parte ${numeroParte}: desde segundo ${tiempoInicio} por ${duracionPorParte}s`);
        log.detalle(`Archivo de salida: ${rutaArchivoSalida}`);

        // ==============================================
        // COMANDO FFMPEG
        // ==============================================
        const comando = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionPorParte} ` +
            `-filter:v "setpts=PTS/${velocidad}" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${rutaArchivoSalida}"`;

        // Ejecutamos
        await ejecutarComando(comando);

        // Verificamos que salió bien
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            return rutaArchivoSalida;
        } else {
            throw new Error('El archivo generado está vacío o es inválido');
        }

    } catch (error) {
        log.error(`Error al generar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
