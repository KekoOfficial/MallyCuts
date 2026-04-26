const { ESTADOS } = require('../config/constants/status');

class JobModel {
  constructor(tipo, datos) {
    this.id = Date.now();
    this.tipo = tipo;
    this.datos = datos;
    this.estado = ESTADOS.PENDIENTE;
    this.progreso = 0;
    this.fechaInicio = null;
    this.fechaFin = null;
  }

  iniciar() {
    this.estado = ESTADOS.PROCESANDO;
    this.fechaInicio = new Date();
  }

  finalizar() {
    this.estado = ESTADOS.COMPLETADO;
    this.fechaFin = new Date();
  }

  fallar(error) {
    this.estado = ESTADOS.FALLIDO;
    this.error = error;
    this.fechaFin = new Date();
  }
}

module.exports = JobModel;
