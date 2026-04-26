function segundosAMinSeg(seg) {
  const m = Math.floor(seg / 60);
  const s = Math.floor(seg % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

function formatoFecha(fecha) {
  return new Date(fecha).toLocaleString('es-PY');
}

function tiempoTranscurrido(inicio, fin = Date.now()) {
  return ((fin - inicio) / 1000).toFixed(2) + 's';
}

module.exports = { segundosAMinSeg, formatoFecha, tiempoTranscurrido };
