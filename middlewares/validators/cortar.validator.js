const { body } = require('express-validator');

const procesar = [
  body('ruta').notEmpty().withMessage('La ruta del archivo es requerida'),
  body('titulo').notEmpty().withMessage('El título es requerido'),
  body('velocidad').optional().isFloat({ min: 0.5, max: 5 }).withMessage('Velocidad inválida'),
  body('duracion').optional().isInt({ min: 10 }).withMessage('Duración inválida'),
];

const preview = [
  body('ruta').notEmpty(),
  body('tiempo').optional().isInt(),
];

const exportar = [
  body('formato').isIn(['mp4', 'mkv', 'avi']).withMessage('Formato no soportado'),
];

module.exports = { procesar, preview, exportar };
