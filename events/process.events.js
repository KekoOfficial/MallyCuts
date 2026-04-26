const EventEmitter = require('events');
const emitter = new EventEmitter();

const EVENTOS = {
  INICIAR: 'process:start',
  PASO: 'process:step',
  FINALIZAR: 'process:complete',
  FALLAR: 'process:fail'
};

function onStart(handler) {
  emitter.on(EVENTOS.INICIAR, handler);
}

function emitStart(id, tipo) {
  emitter.emit(EVENTOS.INICIAR, { id, tipo, fecha: new Date() });
}

function onComplete(handler) {
  emitter.on(EVENTOS.FINALIZAR, handler);
}

function emitComplete(id, resultado) {
  emitter.emit(EVENTOS.FINALIZAR, { id, resultado, fecha: new Date() });
}

function onFail(handler) {
  emitter.on(EVENTOS.FALLAR, handler);
}

function emitFail(id, error) {
  emitter.emit(EVENTOS.FALLAR, { id, error, fecha: new Date() });
}

module.exports = { onStart, emitStart, onComplete, emitComplete, onFail, emitFail };
