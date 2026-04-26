const { validationResult } = require('express-validator');

function formatearErrores(req, res, next) {
  const errores = validationResult(req);
  if (!errores.isEmpty()) {
    return res.status(400).json({
      status: 'error',
      errores: errores.array().map(e => ({ campo: e.param, mensaje: e.msg }))
    });
  }
  next();
}

module.exports = { formatearErrores };
