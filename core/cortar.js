const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../routes/config');
const fs = require('fs').promises;
const { enviarVideo } = require('../routes/enviar');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

const dormir = ms => new Promise(r => setTimeout(r, ms));
const filtroAudio = v => {let f=[],x=v;while(x>2){f.push('atempo=2.0');x/=2}f.push(`atempo=${x}`);return f};

async function extraerYEditarSegmento(ruta, titulo) {
    return new Promise(async (res, rej) => {
        const nombre = limpiarNombreParaArchivo(titulo);
        const salida = path.join(config.CARPETA_TEMPORAL, `${nombre}_%04d.mp4`);

        ffmpeg(ruta)
        .nativeFramerate().withOption('-threads', '2')
        .videoFilters(`setpts=1/${config.VELOCIDAD}*PTS,scale=-2:720`).audioFilters(filtroAudio(config.VELOCIDAD))
        .outputOptions(['-f segment','-segment_time 120','-reset_timestamps 1']).output(salida).run();

        .on('end', async () => {
            let archivos = (await fs.readdir(config.CARPETA_TEMPORAL)).filter(f=>f.startsWith(nombre));
            archivos.sort((a,b)=>a.match(/(\d+)/)[0]-b.match(/(\d+)/)[0]);
            
            for(let i=0;i<archivos.length;i++){
                let r = path.join(config.CARPETA_TEMPORAL, archivos[i]);
                await enviarVideo(r, titulo, i+1, archivos.length);
                if(config.ELIMINAR) await fs.unlink(r);
                await dormir(5000);
            }
            res(true);
        });
    })
}
module.exports = { extraerYEditarSegmento };
