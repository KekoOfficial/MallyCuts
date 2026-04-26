const EventEmitter = require('events');
const emitter = new EventEmitter();

const EVENTOS = {
  CREADO: 'file:created',
  ELIMINADO: 'file:deleted',
  MODIFICADO: 'file:modified',
  MOVIDO: 'file:moved'
};

function onCrear(handler) {
  emitter.on(EVENTOS.CREADO, handler);
}

function emitirCrear(datos) {
  emitter.emit(EVENTOS.CREADO, datos);
}

function onEliminar(handler) {
  emitter.on(EVENTOS.ELIMINADO, handler);
}

function emitirEliminar(datos) {
  emitter.emit(EVENTOS.ELIMINADO, datos);
}

module.exports = { onCrear, emitirCrear, onEliminar, emitirEliminar };
