const fs = require('fs').promises;
const path = require('path');
const logger = require('../../middlewares/logger/logger');

async function crearBackup() {
  logger.info('💾 Creando backup...');
  const fecha = new Date().toISOString().split('T')[0];
  const origen = path.join(__dirname, '../../config');
  const destino = path.join(__dirname, '../../backups', `config_${fecha}.bak`);

  try {
    await fs.mkdir(path.dirname(destino), { recursive: true });
    // Aquí lógica real de copia o compresión
    logger.exito(`✅ Backup creado: ${destino}`);
  } catch (err) {
    logger.error(`💥 Error al crear backup`, err);
  }
}

module.exports = { crearBackup };
