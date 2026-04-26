const path = require('path');

function rutaAbsoluta(rutaRelativa) {
  return path.resolve(__dirname, '../../', rutaRelativa);
}

function unir(...partes) {
  return path.join(...partes);
}

module.exports = { rutaAbsoluta, unir };
