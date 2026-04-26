const { enviarCola } = require('../../services/telegram/queue.service');
const logger = require('../../middlewares/logger/logger');

let colaEnvios = [];
let procesando = false;

async function agregarEnvio(ruta, titulo, parte, total) {
  colaEnvios.push({ ruta, titulo, parte, total });
  logger.info(`📨 Mensaje encolado: ${titulo} (${parte}/${total})`);
  procesarCola();
}

async function procesarCola() {
  if (procesando || colaEnvios.length === 0) return;

  procesando = true;
  const item = colaEnvios.shift();

  try {
    await enviarCola(item.ruta, item.titulo, item.parte, item.total);
  } catch (err) {
    logger.error(`💥 Falló envío`, err);
  } finally {
    procesando = false;
    procesarCola();
  }
}

module.exports = { agregarEnvio, procesarCola };
