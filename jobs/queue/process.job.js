const { worker } = require('../../core/engine/worker.engine');
const { pipelineCorte } = require('../../core/pipeline/video.pipeline');
const logger = require('../../middlewares/logger/logger');

async function procesarEnCola(ruta, titulo, opciones = {}) {
  logger.info(`📋 Tarea encolada: ${titulo}`);
  
  return new Promise((resolve, reject) => {
    worker.agregarTarea({
      id: Date.now(),
      ruta,
      titulo,
      opciones,
      tipo: 'VIDEO_PROCESS'
    });

    // Simular escucha de evento
    pipelineCorte(ruta, titulo, opciones)
      .then(res => { logger.exito(`✅ Finalizado: ${titulo}`); resolve(res); })
      .catch(err => { logger.error(`💥 Falló: ${titulo}`, err); reject(err); });
  });
}

module.exports = { procesarEnCola };
