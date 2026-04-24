const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');

/**
 * Corta el vídeo, cambia la velocidad y agrega tu marca de agua
 * @param {string} rutaEntrada - Ruta del archivo original
 * @param {number} numeroParte - Número de la parte a generar
 * @returns {Promise<string|null>} Ruta del archivo generado
 */
function extraerSegmento(rutaEntrada, numeroParte) {
    return new Promise((resolve) => {
        const tiempoInicio = (numeroParte - 1) * config.CLIP_DURATION;
        const rutaSalida = path.join(config.TEMP_FOLDER, `parte_${numeroParte}.mp4`);

        // ⚙️ CONFIGURACIONES QUE PODÉS CAMBIAR A TU GUSTO
        const VELOCIDAD_VIDEO = 1.3;               // Velocidad: 1.25, 1.3, 1.4 (no más de 1.5 para que se entienda)
        const TEXTO_MARCA = "EnseñaEn15";          // PONÉ ACÁ EL NOMBRE DE TU CANAL O TU MARCA
        const TAMANIO_TEXTO = 22;                  // Tamaño de la letra
        const COLOR_TEXTO = "white";               // Color: white, black, yellow, cyan, etc.
        const TRANSPARENCIA_TEXTO = "0.8";         // 1 = opaco total, 0 = transparente total
        const POSICION_X = "15";                   // Distancia desde el borde izquierdo (en píxeles)
        const POSICION_Y = "15";                   // Distancia desde el borde superior (en píxeles)
        // Si querés ponerlo ABAJO A LA DERECHA: POSICION_X = "main_w-text_w-15" y POSICION_Y = "main_h-text_h-15"

        // 🎯 FILTROS APLICADOS AL VIDEO
        // 1. Cambia la velocidad del video
        // 2. Cambia la velocidad del audio para que coincida
        // 3. Agrega tu texto/marca de agua
        const FILTROS_VIDEO = `
            setpts=${1 / VELOCIDAD_VIDEO}*PTS,
            atempo=${VELOCIDAD_VIDEO},
            drawtext=
                text='${TEXTO_MARCA}':
                x=${POSICION_X}:
                y=${POSICION_Y}:
                fontsize=${TAMANIO_TEXTO}:
                fontcolor=${COLOR_TEXTO}@${TRANSPARENCIA_TEXTO}:
                fontfile=/system/fonts/Roboto-Regular.ttf:
                box=1:
                boxcolor=black@0.3:
                boxborderw=3
        `.replace(/\s+/g, ' ').trim();

        // Comando completo de FFmpeg
        const comandoFFmpeg = [
            '-y',
            '-ss', tiempoInicio.toString(),
            '-i', rutaEntrada,
            '-t', config.CLIP_DURATION.toString(),
            '-vf', FILTROS_VIDEO,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', '2M',
            '-b:a', '128k',
            '-preset', 'fast',
            '-avoid_negative_ts', 'make_zero',
            '-movflags', '+faststart',
            '-hide_banner',
            '-loglevel', 'error',
            rutaSalida
        ];

        execFile('ffmpeg', comandoFFmpeg, {
            maxBuffer: 200 * 1024 * 1024,
            timeout: 180000
        }, (error, stdout, stderr) => {
            if (error) {
                console.error(`❌ Error al generar parte ${numeroParte}: ${error.message}`);
                return resolve(null);
            }

            if (fs.existsSync(rutaSalida)) {
                const datosArchivo = fs.statSync(rutaSalida);
                const tamañoMB = (datosArchivo.size / 1024 / 1024).toFixed(2);

                if (datosArchivo.size > 1000) {
                    console.log(`✅ Parte ${numeroParte} generada | Velocidad: ${VELOCIDAD_VIDEO}x | Marca: "${TEXTO_MARCA}" | Tamaño: ${tamañoMB} MB`);
                    resolve(rutaSalida);
                } else {
                    console.error(`⚠️ Parte ${numeroParte} vacía o dañada`);
                    if (fs.existsSync(rutaSalida)) fs.unlinkSync(rutaSalida);
                    resolve(null);
                }
            } else {
                console.error(`❌ No se pudo crear la parte ${numeroParte}`);
                resolve(null);
            }
        });
    });
}

module.exports = { extraerSegmento };
