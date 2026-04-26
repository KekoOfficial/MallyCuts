function limpiarNombreParaArchivo(texto) {
  return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9 ]/g, '_').replace(/\s+/g, '_').substring(0, 50);
}

function truncate(str, max = 50) {
  return str.length > max ? str.substring(0, max) + '...' : str;
}

module.exports = { limpiarNombreParaArchivo, truncate };
