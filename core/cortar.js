// ✂️ MÓDULO DE CORTE Y PROCESAMIENTO DE VIDEOS
// Incluye marca de agua, velocidad y corte

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');

// Importamos módulos
const log = require('../js/logger');
const config = require('../config');

// Convertimos exec a promesa
const ejecutarComando = util.promisify(exec);

async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo) {
    try {
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo original no existe: ${rutaOriginal}`);
        }

        // Tomamos datos de config.js
        const carpetaSalida = config.CARPETA_TEMPORAL;
        const duracionPorParte = config.DURACION_POR_PARTE;
        const velocidad = config.VELOCIDAD_VIDEO;
        const marcaAgua = config.TEXTO_MARCA_AGUA || "EnseñaEn15"; // 👈 Tu marca

        if (!carpetaSalida || typeof carpetaSalida !== 'string') {
            throw new Error("Ruta CARPETA_TEMPORAL no definida");
        }

        // Calculamos tiempos
        const tiempoInicio = (numeroParte - 1) * duracionPorParte;

        // Nombre y ruta
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_parte_${numeroParte}.mp4`;
        const rutaArchivoSalida = path.join(carpetaSalida, nombreArchivoSalida);

        log.detalle(`Generando parte ${numeroParte}: desde ${tiempoInicio}s por ${duracionPorParte}s`);
        log.detalle(`Archivo salida: ${rutaArchivoSalida}`);
        log.detalle(`Aplicando marca de agua: ${marcaAgua}`);

        // ==============================================
        // 💡 AQUÍ ESTÁ LA MAGIA: AGREGAMOS LA MARCA
        // ==============================================
        // drawtext = texto en pantalla
        // x y w = posición esquina inferior derecha
        // fontsize = tamaño, color = blanco
        const comando = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionPorParte} ` +
            `-filter:v "setpts=PTS/${velocidad}, drawtext=text='${marcaAgua}':fontfile=/system/fonts/Roboto-Regular.ttf:fontsize=24:fontcolor=white@0.8:x=w-tw-10:y=h-th-10" ` +
            `-filter:a "atempo=${velocidad}" ` +
            `-c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k "${rutaArchivoSalida}"`;

        // Ejecutar
        await ejecutarComando(comando);

        // Verificar
        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            return rutaArchivoSalida;
        } else {
            throw new Error('Archivo generado vacío o incorrecto');
        }

    } catch (error) {
        log.error(`Error al generar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
