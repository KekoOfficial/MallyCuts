class UserModel {
  constructor(username, email, rol = 'USER') {
    this.id = Date.now();
    this.username = username;
    this.email = email;
    this.rol = rol;
    this.activo = true;
    this.fechaRegistro = new Date();
  }

  tieneRol(roles) {
    return roles.includes(this.rol);
  }
}

module.exports = UserModel;
