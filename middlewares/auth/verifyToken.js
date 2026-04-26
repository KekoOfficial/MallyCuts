const jwt = require('jsonwebtoken');
const { ERRORES } = require('../../config/constants/errors');

function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(403).json({ error: ERRORES.PERMISO_DENEGADO, mensaje: 'Token requerido' });
  }

  jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
    if (err) {
      return res.status(401).json({ error: ERRORES.PERMISO_DENEGADO, mensaje: 'Token inválido' });
    }
    req.user = decoded;
    next();
  });
}

module.exports = verifyToken;
