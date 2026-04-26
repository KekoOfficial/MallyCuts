const os = require('os');
const logger = require('../../middlewares/logger/logger');
const { infoSistema } = require('../../utils/system/os');

function monitorearSistema() {
  const info = infoSistema();
  const usoMemoria = ((info.memoriaTotal - info.memoriaLibre) / info.memoriaTotal * 100).toFixed(1);

  logger.separador();
  logger.info(`📊 MONITOREO DEL SISTEMA`);
  logger.info(`💻 CPU: ${info.cpus} núcleos`);
  logger.info(`🧠 RAM: ${usoMemoria}% en uso`);
  logger.info(`🖥️  Plataforma: ${info.plataforma}`);
  logger.separador();
}

// Ejecutar cada 5 minutos
// setInterval(monitorearSistema, 300000);

module.exports = { monitorearSistema };
