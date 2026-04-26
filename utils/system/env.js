function get(key, defecto = null) {
  return process.env[key] || defecto;
}

function esProduccion() {
  return process.env.NODE_ENV === 'production';
}

module.exports = { get, esProduccion };
