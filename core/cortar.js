const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');

// ⚡ EXTRAER SEGMENTO - VELOCIDAD MÁXIMA
function extraerSegmento(rutaEntrada, numeroParte) {
    return new Promise((resolve, reject) => {
        // Calcular segundo de inicio
        const inicio = (numeroParte - 1) * config.CLIP_DURATION;
        const rutaSalida = path.join(config.TEMP_FOLDER, `parte_${numeroParte}.mp4`);

        // Comando optimizado, usa copia directa sin recodificar
        const comando = [
            '-y',
            '-ss', inicio.toString(),
            '-i', rutaEntrada,
            '-t', config.CLIP_DURATION.toString(),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-movflags', '+faststart',
            rutaSalida
        ];

        execFile('ffmpeg', comando, {
            maxBuffer: 1024 * 1024 * 100 // 100MB de buffer para archivos grandes
        }, (error) => {
            if (error) {
                console.error(`❌ Error al cortar parte ${numeroParte}:`, error.message);
                return resolve(null);
            }
            resolve(rutaSalida);
        });
    });
}

module.exports = { extraerSegmento };
