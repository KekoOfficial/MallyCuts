const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');
const config = require('../config');

function extraerSegmento(rutaEntrada, numeroParte) {
    return new Promise((resolve) => {
        const tiempoInicio = (numeroParte - 1) * config.CLIP_DURATION;
        const rutaSalida = path.join(config.TEMP_FOLDER, `parte_${numeroParte}.mp4`);

        const comandoFFmpeg = [
            '-y',
            '-ss', tiempoInicio.toString(),
            '-i', rutaEntrada,
            '-t', config.CLIP_DURATION.toString(),
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-fflags', '+genpts+igndts',
            '-async', '1',
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
                console.error(`❌ Error al cortar parte ${numeroParte}: ${error.message}`);
                return resolve(null);
            }

            if (fs.existsSync(rutaSalida)) {
                const datosArchivo = fs.statSync(rutaSalida);
                const tamañoMB = (datosArchivo.size / 1024 / 1024).toFixed(2);

                if (datosArchivo.size > 1000) {
                    console.log(`✅ Parte ${numeroParte} lista | Tamaño: ${tamañoMB} MB`);
                    resolve(rutaSalida);
                } else {
                    console.error(`⚠️ Parte ${numeroParte} vacía`);
                    if (fs.existsSync(rutaSalida)) fs.unlinkSync(rutaSalida);
                    resolve(null);
                }
            } else {
                console.error(`❌ No se creó la parte ${numeroParte}`);
                resolve(null);
            }
        });
    });
}

module.exports = { extraerSegmento };
