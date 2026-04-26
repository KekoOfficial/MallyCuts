const logger = require('./logger');

function requestLogger(req, res, next) {
  const { method, url, ip } = req;
  logger.info(`📥 ${method} ${url} - ${ip}`);
  
  // Log al finalizar
  res.on('finish', () => {
    logger.exito(`📤 ${method} ${url} -> ${res.statusCode}`);
  });

  next();
}

module.exports = requestLogger;
