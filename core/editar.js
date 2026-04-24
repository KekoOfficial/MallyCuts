// ✨ MÓDULO DE EDICIÓN Y PROCESAMIENTO GLOBAL
// Aplica marca de agua y velocidad al video completo

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
 * Procesa el video completo aplicando efectos globales
 * @param {string} rutaOriginal - Ruta del archivo fuente
 * @param {string} tituloVideo - Título para nombrar el archivo editado
 * @returns {Promise<string|null>} Ruta del archivo editado final
 */
async function procesarVideoCompleto(rutaOriginal, tituloVideo) {
    try {
        // Verificar archivo de entrada
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // Cargar parámetros de configuración
        const carpetaSalida = config.CARPETA_TEMPORAL;
        const velocidad = config.VELOCIDAD_VIDEO;
        const marcaAgua = config.TEXTO_MARCA_AGUA || "MallyCuts";

        // Validación de rutas
        if (!carpetaSalida || typeof carpetaSalida !== 'string') {
            throw new Error("Ruta de carpeta temporal no definida correctamente");
        }

        // Generar nombre y ruta del archivo final editado
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_EDITADO.mp4`;
        const rutaArchivoSalida = path.join(carpetaSalida, nombreArchivoSalida);

        // Logs informativos
        log.info('🎬 INICIANDO EDICIÓN GLOBAL DEL VIDEO');
        log.detalle(`Archivo destino: ${rutaArchivoSalida}`);
        log.detalle(`Velocidad: x${velocidad}`);
        log.detalle(`Marca de agua: ${marcaAgua} (CENTRO)`);

        // ==============================================
        // 🎬 COMANDO FFmpeg DE EDICIÓN
        // ==============================================
        // Aplica:
        // 1. Cambio de velocidad (audio y video)
        // 2. Marca de agua en el centro, grande y con borde

        const comando = `ffmpeg -y -i "${rutaOriginal}" ` +
            `-filter:v "setpts=PTS/${velocidad}, drawtext=text='${marcaAgua}':fontfile=/system/fonts/Roboto-Regular.ttf:fontsize=40:fontcolor=white@0.8:bordercolor=black@1.0:borderw=2:x=(w-text_w)/2:y=(h-text_h)/2" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${rutaArchivoSalida}"`;

        // Ejecutar proceso
        await ejecutarComando(comando);

        // Verificación de integridad
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            log.exito('✅ Edición completada. Video listo para corte.');
            return rutaArchivoSalida;
        } else {
            throw new Error('El archivo editado se generó vacío o es inválido');
        }

    } catch (error) {
        log.error('Error durante la edición global', error);
        return null;
    }
}

module.exports = {
    procesarVideoCompleto
};
