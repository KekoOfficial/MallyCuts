// 🛠️ FUNCIONES AUXILIARES Y UTILIDADES
const fs = require('fs');
const { execFile } = require('child_process');
const log = require('../js/logger');

/**
 * Crea todas las carpetas que se necesitan si no existen
 * @param {object} config - Objeto con las rutas de configuración
 */
function crearCarpetasNecesarias(config) {
    const carpetas = [
        config.ORIGINAL_FOLDER,
        config.TEMP_FOLDER,
        config.INPUT_FOLDER,
        config.TEMP_UPLOAD_FOLDER
    ];

    carpetas.forEach(ruta => {
        if (!ruta) return;
        try {
            if (!fs.existsSync(ruta)) {
                fs.mkdirSync(ruta, { recursive: true, mode: 0o777 });
                log.exito(`Carpeta creada: ${ruta}`);
            } else {
                log.detalle(`Carpeta ya disponible: ${ruta}`);
            }
        } catch (error) {
            log.error(`No se pudo acceder o crear la carpeta: ${ruta}`, error);
        }
    });
}

/**
 * Obtiene la duración total de un video en segundos
 * @param {string} rutaArchivo - Ruta del archivo de video
 * @returns {Promise<number>} Duración en segundos
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        const comando = [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            rutaArchivo
        ];

        execFile('ffprobe', comando, { timeout: 300000 }, (error, stdout, stderr) => {
            if (error || !stdout) {
                return reject(new Error('No se pudo leer la duración del video'));
            }
            const duracion = parseFloat(stdout.trim());
            resolve(duracion);
        });
    });
}

module.exports = {
    crearCarpetasNecesarias,
    obtenerDuracionVideo
};
