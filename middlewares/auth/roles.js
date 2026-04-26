function tieneRol(...rolesPermitidos) {
  return (req, res, next) => {
    if (!req.user || !rolesPermitidos.includes(req.user.rol)) {
      return res.status(403).json({
        error: 'ACCESO_DENEGADO',
        mensaje: 'No tienes permisos para esta acción'
      });
    }
    next();
  };
}

module.exports = { tieneRol };
