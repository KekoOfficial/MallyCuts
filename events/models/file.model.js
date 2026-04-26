class FileModel {
  constructor(nombre, ruta, tamaño, tipo) {
    this.id = Date.now();
    this.nombre = nombre;
    this.ruta = ruta;
    this.tamaño = tamaño;
    this.tipo = tipo;
    this.fechaCreacion = new Date();
    this.estado = 'ACTIVE';
  }

  toJSON() {
    return { ...this };
  }
}

module.exports = FileModel;
