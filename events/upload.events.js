const EventEmitter = require('events');
const emitter = new EventEmitter();

const EVENTOS = {
  INICIADO: 'upload:start',
  PROGRESO: 'upload:progress',
  FINALIZADO: 'upload:complete',
  ERROR: 'upload:error'
};

function onIniciado(handler) {
  emitter.on(EVENTOS.INICIADO, handler);
}

function emitirIniciado(datos) {
  emitter.emit(EVENTOS.INICIADO, datos);
}

function onFinalizado(handler) {
  emitter.on(EVENTOS.FINALIZADO, handler);
}

function emitirFinalizado(datos) {
  emitter.emit(EVENTOS.FINALIZADO, datos);
}

module.exports = { onIniciado, emitirIniciado, onFinalizado, emitirFinalizado };
