// 🛠️ FUNCIONES AUXILIARES Y UTILIDADES GENERALES
// Aquí se encuentran las funciones que se usan en varias partes del sistema

const fs = require('fs');
const { execFile } = require('child_process');
const log = require('../js/logger');

/**
 * Crea todas las carpetas necesarias para el funcionamiento del sistema
 * Si alguna carpeta ya existe, solo la verifica y muestra el mensaje correspondiente
 * @param {object} config - Objeto con las rutas definidas en la configuración
 */
function crearCarpetasNecesarias(config) {
    // Lista de carpetas que se deben crear
    const carpetas = [
        config.ORIGINAL_FOLDER,
        config.TEMP_FOLDER,
        config.INPUT_FOLDER,
        config.TEMP_UPLOAD_FOLDER
    ];

    // Recorremos cada ruta y la creamos si no existe
    carpetas.forEach(rutaCarpeta => {
        // Si la ruta no está definida, pasamos de largo
        if (!rutaCarpeta) return;

        try {
            // Verificamos si la carpeta ya existe
            if (!fs.existsSync(rutaCarpeta)) {
                // Creamos la carpeta y todas las subcarpetas necesarias
                fs.mkdirSync(rutaCarpeta, { recursive: true, mode: 0o777 });
                log.exito(`Carpeta creada correctamente: ${rutaCarpeta}`);
            } else {
                log.detalle(`Carpeta ya disponible: ${rutaCarpeta}`);
            }
        } catch (error) {
            log.error(`No se pudo crear o acceder a la carpeta: ${rutaCarpeta}`, error);
        }
    });
}

/**
 * Obtiene la duración total de un archivo de video expresada en segundos
 * Usa la herramienta ffprobe para leer los datos del archivo
 * @param {string} rutaArchivo - Ruta completa del archivo de video
 * @returns {Promise<number>} Duración del video en segundos
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        // Comando para obtener solo la duración del video
        const comando = [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            rutaArchivo
        ];

        // Ejecutamos el comando con un tiempo máximo de espera de 5 minutos
        execFile('ffprobe', comando, { timeout: 300000 }, (error, stdout, stderr) => {
            // Si hubo un error o no se obtuvo ningún dato
            if (error || !stdout) {
                return reject(new Error('No se pudo leer la duración del archivo de video'));
            }

            // Convertimos el resultado a número decimal
            const duracionEnSegundos = parseFloat(stdout.trim());
            
            // Verificamos que el valor obtenido sea válido
            if (isNaN(duracionEnSegundos) || duracionEnSegundos <= 0) {
                return reject(new Error('La duración del video es inválida o no se pudo leer correctamente'));
            }

            resolve(duracionEnSegundos);
        });
    });
}

/**
 * Convierte una duración en segundos a un formato legible de horas, minutos y segundos
 * @param {number} segundos - Duración en segundos
 * @returns {string} Cadena de texto con el formato "HHh MMm SSs"
 */
function formatoDuracion(segundos) {
    const horas = Math.floor(segundos / 3600);
    const minutos = Math.floor((segundos % 3600) / 60);
    const segRestantes = Math.floor(segundos % 60);

    let texto = '';
    if (horas > 0) texto += `${horas}h `;
    if (minutos > 0 || horas > 0) texto += `${minutos}m `;
    texto += `${segRestantes}s`;

    return texto.trim();
}

/**
 * Verifica si un archivo existe y tiene un tamaño mayor a cero
 * @param {string} rutaArchivo - Ruta del archivo a verificar
 * @returns {boolean} Verdadero si el archivo es válido, falso en caso contrario
 */
function archivoEsValido(rutaArchivo) {
    try {
        if (!fs.existsSync(rutaArchivo)) return false;
        
        const estadisticas = fs.statSync(rutaArchivo);
        return estadisticas.isFile() && estadisticas.size > 0;
    } catch (error) {
        log.error(`Error al verificar el archivo: ${rutaArchivo}`, error);
        return false;
    }
}

/**
 * Obtiene el tamaño de un archivo expresado en megabytes
 * @param {string} rutaArchivo - Ruta del archivo
 * @returns {string} Tamaño formateado con dos decimales
 */
function obtenerTamanoArchivoMB(rutaArchivo) {
    try {
        if (!archivoEsValido(rutaArchivo)) return '0.00 MB';
        
        const tamanoBytes = fs.statSync(rutaArchivo).size;
        const tamanoMB = tamanoBytes / (1024 * 1024);
        
        return `${tamanoMB.toFixed(2)} MB`;
    } catch (error) {
        log.error(`No se pudo obtener el tamaño del archivo: ${rutaArchivo}`, error);
        return 'Desconocido';
    }
}

// Exportamos todas las funciones para poder usarlas en otros archivos
module.exports = {
    crearCarpetasNecesarias,
    obtenerDuracionVideo,
    formatoDuracion,
    archivoEsValido,
    obtenerTamanoArchivoMB
};
