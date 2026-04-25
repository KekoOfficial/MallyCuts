const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const log = require('../js/logger');
const config = require('../routes/config');
const fs = require('fs').promises;
const { enviarVideo } = require('../routes/enviar');
const { limpiarNombreParaArchivo } = require('../routes/titulo');

const dormir = ms => new Promise(r => setTimeout(r, ms));
const audio = v => {let f=[],x=v;while(x>2){f.push('atempo=2.0');x/=2}f.push(`atempo=${x}`);return f};

async function extraerYEditarSegmento(ruta, titulo) {
  return new Promise(async (res, rej) => {
    const nom = limpiarNombreParaArchivo(titulo);
    const out = path.join(config.CARPETA_TEMPORAL, `${nom}_%04d.mp4`);

    const cmd = ffmpeg(ruta)
    .nativeFramerate().withOption('-threads', '2')
    .videoFilters(`setpts=1/${config.VELOCIDAD}*PTS,scale=-2:720`).audioFilters(audio(config.VELOCIDAD))
    .outputOptions(['-f segment','-segment_time 120','-reset_timestamps 1']).output(out);

    cmd.on('end', async () => {
      let arch = (await fs.readdir(config.CARPETA_TEMPORAL)).filter(f=>f.startsWith(nom));
      arch.sort((a,b)=>a.match(/\d+/)[0]-b.match(/\d+/)[0]);
      
      for(let i=0;i<arch.length;i++){
        let r = path.join(config.CARPETA_TEMPORAL, arch[i]);
        await enviarVideo(r, titulo, i+1, arch.length);
        if(config.ELIMINAR) await fs.unlink(r);
        await dormir(5000);
      }
      res(true);
    });
    cmd.on('error', rej);
    cmd.run();
  })
}
module.exports = { extraerYEditarSegmento };
