const config = require('../../config/upload');
const { ERRORES } = require('../../config/constants/errors');

function validarUpload(req, res, next) {
  if (!req.file) {
    return res.status(400).json({ error: ERRORES.ARCHIVO_NO_ENCONTRADO });
  }

  if (!config.PERMITIDOS.includes(req.file.mimetype)) {
    return res.status(400).json({ error: ERRORES.FORMATO_INVALIDO });
  }

  const mb = req.file.size / (1024 * 1024);
  if (mb > config.MAX_SIZE_MB) {
    return res.status(400).json({ error: ERRORES.LIMITE_EXCEDIDO });
  }

  next();
}

module.exports = validarUpload;
