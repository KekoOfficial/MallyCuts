// 📋 SISTEMA DE REGISTRO PERSONALIZADO
// Mensajes claros, con colores y emojis, sin información innecesaria

// Definimos los códigos de colores para que se vea más ordenado
const COLORES = {
    exito: '\x1b[32m',    // Verde
    error: '\x1b[31m',    // Rojo
    aviso: '\x1b[33m',    // Amarillo
    info: '\x1b[34m',     // Azul
    detalle: '\x1b[90m',  // Gris
    reset: '\x1b[0m'      // Volver al color normal
};

/**
 * Mensaje de éxito
 * @param {string} mensaje - Texto a mostrar
 */
function exito(mensaje) {
    const fecha = new Date().toLocaleString();
    console.log(`${COLORES.exito}✅ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Mensaje de error
 * @param {string} mensaje - Texto a mostrar
 * @param {Error} [error] - Objeto de error opcional
 */
function error(mensaje, error = null) {
    const fecha = new Date().toLocaleString();
    console.log(`${COLORES.error}❌ [${fecha}] ${mensaje}${COLORES.reset}`);
    if (error) {
        console.log(`${COLORES.detalle}   Detalle: ${error.message}${COLORES.reset}`);
    }
}

/**
 * Mensaje de aviso o advertencia
 * @param {string} mensaje - Texto a mostrar
 */
function aviso(mensaje) {
    const fecha = new Date().toLocaleString();
    console.log(`${COLORES.aviso}⚠️ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Mensaje de información general
 * @param {string} mensaje - Texto a mostrar
 */
function info(mensaje) {
    const fecha = new Date().toLocaleString();
    console.log(`${COLORES.info}ℹ️ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Mensaje de detalle o proceso interno
 * @param {string} mensaje - Texto a mostrar
 */
function detalle(mensaje) {
    const fecha = new Date().toLocaleString();
    console.log(`${COLORES.detalle}🔍 [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Línea separadora para dividir procesos
 * @param {string} titulo - Texto opcional para poner en el centro
 */
function separador(titulo = '') {
    const linea = '='.repeat(70);
    if (titulo) {
        const espacios = Math.floor((70 - titulo.length) / 2);
        console.log(`\n${COLORES.info}${' '.repeat(espacios)}${titulo}${COLORES.reset}`);
        console.log(`${COLORES.info}${linea}${COLORES.reset}\n`);
    } else {
        console.log(`\n${COLORES.info}${linea}${COLORES.reset}\n`);
    }
}

// Exportamos todas las funciones para usarlas en cualquier parte del proyecto
module.exports = {
    exito,
    error,
    aviso,
    info,
    detalle,
    separador
};
