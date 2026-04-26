const logger = require('../logger/logger');
const { ERRORES } = require('../../config/constants/errors');

function manejadorErrores(err, req, res, next) {
  logger.error('💥 Error capturado', err);

  const codigo = err.status || 500;
  const tipo = err.tipo || ERRORES.ERROR_GENERAL;

  res.status(codigo).json({
    status: 'error',
    error: tipo,
    mensaje: err.message || 'Error interno del servidor',
    codigo
  });
}

module.exports = manejadorErrores;
