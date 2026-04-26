const { pipelineSubida } = require('../../core/pipeline/upload.pipeline');
const logger = require('../../middlewares/logger/logger');

async function jobSubidaArchivo(file, carpeta = 'temp') {
  logger.info(`📤 Iniciando job de subida...`);
  try {
    const resultado = await pipelineSubida(file, carpeta);
    logger.exito(`✅ Subida completada: ${resultado.nombre}`);
    return resultado;
  } catch (error) {
    logger.error(`💥 Falló la subida`, error);
    throw error;
  }
}

module.exports = { jobSubidaArchivo };
