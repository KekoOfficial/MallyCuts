// ✂️ MÓDULO DE CORTE Y DIVISIÓN
// Diseñado para trabajar sobre videos ya editados

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');

const log = require('../js/logger');
const config = require('../config');

const ejecutarComando = util.promisify(exec);

async function extraerSegmento(rutaOriginal, numeroParte, tituloVideo) {
    try {
        if (!fs.existsSync(rutaOriginal)) {
            throw new Error(`El archivo fuente no existe: ${rutaOriginal}`);
        }

        const carpetaSalida = config.CARPETA_TEMPORAL;
        const duracionPorParte = config.DURACION_POR_PARTE || 120;

        if (!carpetaSalida || typeof carpetaSalida !== 'string') {
            throw new Error("Ruta de carpeta temporal no definida");
        }

        const tiempoInicio = (numeroParte - 1) * duracionPorParte;
        const nombreLimpio = tituloVideo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        const nombreArchivoSalida = `${nombreLimpio}_parte_${numeroParte}.mp4`;
        const rutaArchivoSalida = path.join(carpetaSalida, nombreArchivoSalida);

        log.detalle(`Cortando parte ${numeroParte}: desde ${tiempoInicio}s por ${duracionPorParte}s`);

        // Comando de corte simple y rápido
        const comando = `ffmpeg -y -i "${rutaOriginal}" -ss ${tiempoInicio} -t ${duracionPorParte} -c copy "${rutaArchivoSalida}"`;

        await ejecutarComando(comando);

        if (fs.existsSync(rutaArchivoSalida) && fs.statSync(rutaArchivoSalida).size > 1024) {
            return rutaArchivoSalida;
        } else {
            throw new Error('El archivo generado está vacío');
        }

    } catch (error) {
        log.error(`Error al cortar la parte ${numeroParte}`, error);
        return null;
    }
}

module.exports = {
    extraerSegmento
};
