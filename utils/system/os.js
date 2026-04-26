const os = require('os');

function infoSistema() {
  return {
    plataforma: os.platform(),
    arquitectura: os.arch(),
    cpus: os.cpus().length,
    memoriaLibre: os.freemem(),
    memoriaTotal: os.totalmem()
  };
}

module.exports = { infoSistema };
