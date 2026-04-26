const fs = require('fs').promises;
const path = require('path');
const { PATHS } = require('../../config/constants/paths');
const logger = require('../../middlewares/logger/logger');

async function limpiarArchivosTemporales() {
  logger.info('🧹 Iniciando limpieza automática...');
  const edadMax = 2 * 60 * 60 * 1000; // 2 horas

  try {
    const archivos = await fs.readdir(PATHS.TEMP);
    let eliminados = 0;

    for (const arch of archivos) {
      const ruta = path.join(PATHS.TEMP, arch);
      const stats = await fs.stat(ruta);
      if (Date.now() - stats.ctimeMs > edadMax) {
        await fs.unlink(ruta);
        eliminados++;
      }
    }

    logger.exito(`🧹 Limpieza finalizada. Eliminados: ${eliminados}`);
  } catch (err) {
    logger.error(`💥 Error en limpieza`, err);
  }
}

// Ejecutar cada hora
// setInterval(limpiarArchivosTemporales, 3600000);

module.exports = { limpiarArchivosTemporales };
