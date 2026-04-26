const { body } = require('express-validator');

const procesar = [
  body('ruta').exists().withMessage('Ruta es obligatoria'),
  body('titulo').exists().withMessage('Título es obligatorio'),
];

const info = [
  body('ruta').exists().withMessage('Debes indicar el archivo'),
];

module.exports = { procesar, info };
