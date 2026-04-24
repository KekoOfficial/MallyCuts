const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');
const { extraerSegmento } = require('./cortar');
// ✅ CORREGIDO: Ahora importamos el archivo correcto
const { enviarADosCanales } = require('./enviar');

/**
 * Procesa un enlace completo: obtiene título, descarga, corta y envía
 * @param {string} enlace - Enlace del video de TikTok, YouTube, etc.
 * @returns {Promise<boolean>} Estado del proceso
 */
async function procesarEnlace(enlace) {
    console.log("\n" + "=".repeat(60));
    console.log("🔗 PROCESANDO ENLACE RECIBIDO");
    console.log(`🌐 Enlace: ${enlace}`);
    console.log("=".repeat(60));

    try {
        // 📝 PASO 1: Obtener el título automáticamente del video
        console.log("📋 Obteniendo título del contenido...");
        const tituloOriginal = await obtenerTitulo(enlace);
        // Limpiamos el título para que no tenga símbolos que den problemas
        const tituloLimpio = tituloOriginal.replace(/[<>:"/\\|?*\n\r]/g, ' ').trim().substring(0, 100);
        console.log(`✅ Título obtenido: "${tituloLimpio}"`);

        // ⬇️ PASO 2: Descargar el video
        console.log("\n⬇️ Iniciando descarga del video...");
        const rutaVideoDescargado = path.join(config.ORIGINAL_FOLDER, `${tituloLimpio}.mp4`);
        await descargarVideo(enlace, rutaVideoDescargado);
        console.log("✅ Video descargado correctamente");

        // 🧮 PASO 3: Calcular duración y cantidad de partes
        console.log("\n⏱️ Calculando duración del video...");
        const duracionTotal = await obtenerDuracionVideo(rutaVideoDescargado);
        const cantidadPartes = Math.floor(duracionTotal / config.CLIP_DURATION) + 1;
        console.log(`ℹ️ Duración total: ${Math.round(duracionTotal)} segundos | Se generarán ${cantidadPartes} partes de ${config.CLIP_DURATION} segundos cada una`);

        // ✂️ PASO 4: Generar todas las partes
        console.log("\n✂️ Iniciando corte y procesamiento de las partes...");
        const listaDePartes = [];

        for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
            console.log(`🔄 Procesando parte ${numeroParte}/${cantidadPartes}`);
            const rutaParte = await extraerSegmento(rutaVideoDescargado, numeroParte);
            
            if (rutaParte) {
                listaDePartes.push({
                    numero: numeroParte,
                    ruta: rutaParte
                });
            }
        }

        console.log(`✅ Se generaron ${listaDePartes.length} partes válidas`);

        // 📤 PASO 5: Enviar todas las partes a los DOS CANALES automáticamente
        console.log("\n📤 Iniciando envío de contenido a los canales...");
        for (const parte of listaDePartes) {
            // Mensaje personalizado con el título obtenido automáticamente
            const mensaje = `🎬 <b>${tituloLimpio}</b>
📌 <b>Parte:</b> ${parte.numero} de ${listaDePartes.length}
✅ Contenido procesado y verificado
🔗 <b>Canal:</b> ${config.CANAL_PUBLICO.NOMBRE}`;

            // Usamos la función que creamos
            await enviarADosCanales(parte.ruta, mensaje, parte.numero);

            // Eliminamos la parte después de enviarla
            if (fs.existsSync(parte.ruta)) {
                fs.unlinkSync(parte.ruta);
            }

            // Pequeña pausa para no saturar
            await new Promise(resolve => setTimeout(resolve, 1500));
        }

        // 🧹 PASO 6: Limpieza final
        if (config.BORRAR_ARCHIVOS_DESPUES) {
            if (fs.existsSync(rutaVideoDescargado)) {
                fs.unlinkSync(rutaVideoDescargado);
                console.log("🗑️ Video original descargado eliminado");
            }
        }

        console.log("\n" + "=".repeat(60));
        console.log("✅ ¡PROCESO COMPLETADO AL 100%!");
        console.log("✅ Todo enviado correctamente a tus canales");
        console.log("=".repeat(60) + "\n");

        return true;

    } catch (error) {
        console.error("\n❌ ERROR EN EL PROCESO:", error.message);
        return false;
    }
}

/**
 * Obtiene el título del video usando yt-dlp
 */
function obtenerTitulo(enlace) {
    return new Promise((resolve, reject) => {
        execFile('yt-dlp', [
            '--print', 'title',
            '--no-warnings',
            '--no-playlist',
            enlace
        ], (error, stdout, stderr) => {
            if (error || !stdout.trim()) {
                return reject(new Error("No se pudo obtener el título del video"));
            }
            resolve(stdout.trim());
        });
    });
}

/**
 * Descarga el video en la mejor calidad disponible
 */
function descargarVideo(enlace, rutaDestino) {
    return new Promise((resolve, reject) => {
        execFile('yt-dlp', [
            '-o', rutaDestino,
            '-f', 'best[ext=mp4]/best',
            '--no-warnings',
            '--no-playlist',
            enlace
        ], (error, stdout, stderr) => {
            if (error) {
                return reject(new Error("Error al descargar: " + error.message));
            }
            if (fs.existsSync(rutaDestino)) {
                resolve();
            } else {
                reject(new Error("El archivo descargado no se encontró"));
            }
        });
    });
}

/**
 * Obtiene la duración total del video en segundos
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        execFile('ffprobe', [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            rutaArchivo
        ], (error, stdout) => {
            if (error || !stdout || isNaN(parseFloat(stdout))) {
                return reject(new Error("No se pudo leer la duración del video"));
            }
            resolve(parseFloat(stdout.trim()));
        });
    });
}

module.exports = { procesarEnlace };
