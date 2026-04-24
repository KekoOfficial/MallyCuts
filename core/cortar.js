// ✂️ MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Versión corregida - Compatible con config.js actual

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
 */
async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo) {
    try {
        // Verificar que el archivo existe
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // ==============================================
        // 💡 SOLUCIÓN: Definimos la ruta de salida aquí
        // ==============================================
        // Usamos TEMP_FOLDER que existe en tu config.js
        const carpetaSalida = config.TEMP_FOLDER;
        
        // Verificamos que la carpeta sea un string válido
        if (!carpetaSalida || typeof carpetaSalida !== 'string') {
            throw new Error("Ruta de carpeta temporal no definida correctamente");
        }

        // Tomamos parámetros
        const duracionPorParte = config.DURACION_POR_PARTE || 60;
        const velocidad = config.VELOCIDAD_VIDEO || 1.0;

        // Calculamos tiempos
        const tiempoInicio = (numeroParte - 1) * duracionPorParte;

        // Generamos nombre y ruta completa
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_parte_${numeroParte}.mp4`;
        const rutaArchivoSalida = path.join(carpetaSalida, nombreArchivoSalida);

        // Logs
        log.detalle(`Generando parte ${numeroParte}: desde el segundo ${tiempoInicio} por ${duracionPorParte} segundos`);
        log.detalle(`Archivo de salida: ${rutaArchivoSalida}`);

        // ==============================================
        // COMANDO FFMPEG
        // ==============================================
        const comando = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionPorParte} ` +
            `-filter:v "setpts=PTS/${velocidad}" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${rutaArchivoSalida}"`;

        // Ejecutar
        await ejecutarComando(comando);

        // Verificar resultado
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            return rutaArchivoSalida;
        } else {
            throw new Error('El archivo generado es vacío o incorrecto');
        }

    } catch (error) {
        log.error(`Error al generar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
