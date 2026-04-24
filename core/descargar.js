const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const https = require('https');
const { URL } = require('url');
const config = require('../config');
const { extraerSegmento } = require('./cortar');
const { enviarATelegram } = require('./telegram'); // Asumimos que ya tenés tu función para enviar

/**
 * Descarga el video, obtiene el título y lo prepara para procesar
 * @param {string} enlace - Enlace del video
 * @returns {Promise<boolean>} Resultado del proceso
 */
async function procesarEnlace(enlace) {
    console.log('🔗 Enlace recibido:', enlace);

    try {
        // 📝 PASO 1: OBTENER EL TÍTULO AUTOMÁTICAMENTE
        console.log('📋 Obteniendo título del video...');
        const titulo = await obtenerTituloVideo(enlace);
        console.log(`✅ Título obtenido: "${titulo}"`);

        // Limpiamos el título para que no tenga caracteres que no sirvan en nombres de archivos
        const tituloLimpio = titulo.replace(/[<>:"/\\|?*]/g, '').substring(0, 100);
        const rutaVideoOriginal = path.join(config.ORIGINAL_FOLDER, `${tituloLimpio}.mp4`);

        // ⬇️ PASO 2: DESCARGAR EL VIDEO
        console.log('⬇️ Descargando video...');
        await descargarVideo(enlace, rutaVideoOriginal);
        console.log('✅ Video descargado correctamente');

        // ✂️ PASO 3: PROCESAR Y CORTAR AUTOMÁTICAMENTE
        console.log('✂️ Enviando video a proceso de corte...');
        await procesarVideo(rutaVideoOriginal, tituloLimpio);

        return true;

    } catch (error) {
        console.error('❌ Error en el proceso:', error.message);
        return false;
    }
}

/**
 * Obtiene el título del video desde la página
 * Usa yt-dlp que es la herramienta más potente para esto
 */
function obtenerTituloVideo(enlace) {
    return new Promise((resolve, reject) => {
        execFile('yt-dlp', [
            '--print', 'title',
            '--no-warnings',
            enlace
        ], (error, stdout, stderr) => {
            if (error || !stdout.trim()) {
                return reject(new Error('No se pudo obtener el título del video'));
            }
            resolve(stdout.trim());
        });
    });
}

/**
 * Descarga el video usando yt-dlp
 */
function descargarVideo(enlace, rutaDestino) {
    return new Promise((resolve, reject) => {
        execFile('yt-dlp', [
            '-o', rutaDestino,
            '-f', 'mp4[ext=mp4]',
            '--no-warnings',
            enlace
        ], (error, stdout, stderr) => {
            if (error) {
                return reject(new Error('Error al descargar el video: ' + error.message));
            }
            if (fs.existsSync(rutaDestino)) {
                resolve();
            } else {
                reject(new Error('El archivo descargado no se encuentra'));
            }
        });
    });
}

/**
 * Procesa el video: lo corta, genera fragmentos y envía
 */
async function procesarVideo(rutaVideo, nombreBase) {
    // Obtenemos la duración total del video
    const duracionTotal = await obtenerDuracionVideo(rutaVideo);
    const cantidadPartes = Math.ceil(duracionTotal / config.CLIP_DURATION);

    console.log(`ℹ️ Duración total: ${duracionTotal.toFixed(1)} segundos | Se generarán ${cantidadPartes} partes`);

    // Recorremos todas las partes para generarlas
    const partesGeneradas = [];
    for (let i = 1; i <= cantidadPartes; i++) {
        console.log(`🔄 Generando parte ${i} de ${cantidadPartes}...`);
        const rutaParte = await extraerSegmento(rutaVideo, i);
        
        if (rutaParte) {
            partesGeneradas.push(rutaParte);
            // 📤 Enviamos la parte directamente a Telegram en cuanto se genera
            await enviarATelegram(rutaParte, `${nombreBase} - Parte ${i}`);
        }
    }

    // Limpiamos archivos temporales si querés
    if (config.BORRAR_ARCHIVOS_DESPUES) {
        fs.unlinkSync(rutaVideo);
        partesGeneradas.forEach(ruta => {
            if (fs.existsSync(ruta)) fs.unlinkSync(ruta);
        });
        console.log('🧹 Archivos temporales eliminados');
    }

    console.log('✅ PROCESO FINALIZADO CON ÉXITO');
}

/**
 * Obtiene la duración del video en segundos
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        execFile('ffprobe', [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            rutaArchivo
        ], (error, stdout) => {
            if (error) return reject(error);
            resolve(parseFloat(stdout.trim()));
        });
    });
}

module.exports = { procesarEnlace };
