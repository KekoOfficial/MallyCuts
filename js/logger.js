// 📋 SISTEMA DE REGISTRO DE MENSAJES
// Muestra mensajes organizados, con colores y marca de tiempo

// Códigos de colores para la terminal
const COLORES = {
    exito: '\x1b[32m',    // Verde → Operaciones correctas
    error: '\x1b[31m',    // Rojo → Errores y fallos
    aviso: '\x1b[33m',    // Amarillo → Advertencias o información importante
    info: '\x1b[34m',     // Azul → Información general
    detalle: '\x1b[90m',  // Gris → Datos complementarios o detalles
    reset: '\x1b[0m'      // Restablecer color predeterminado
};

/**
 * Obtiene la fecha y hora actual formateada
 * @returns {string} Fecha y hora en formato legible
 */
function obtenerFechaHora() {
    return new Date().toLocaleString('es-AR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Muestra un mensaje de operación exitosa
 * @param {string} mensaje - Texto que se quiere mostrar
 */
function exito(mensaje) {
    const fecha = obtenerFechaHora();
    console.log(`${COLORES.exito}✅ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Muestra un mensaje de error
 * @param {string} mensaje - Texto que describe el error
 * @param {Error} [error] - Objeto de error opcional para mostrar detalles
 */
function error(mensaje, error = null) {
    const fecha = obtenerFechaHora();
    console.log(`${COLORES.error}❌ [${fecha}] ${mensaje}${COLORES.reset}`);
    
    if (error) {
        console.log(`${COLORES.detalle}   ⚠️ Detalle: ${error.message || error}${COLORES.reset}`);
    }
}

/**
 * Muestra un mensaje de advertencia o información relevante
 * @param {string} mensaje - Texto del aviso
 */
function aviso(mensaje) {
    const fecha = obtenerFechaHora();
    console.log(`${COLORES.aviso}⚠️ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Muestra un mensaje de información general
 * @param {string} mensaje - Texto informativo
 */
function info(mensaje) {
    const fecha = obtenerFechaHora();
    console.log(`${COLORES.info}ℹ️ [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Muestra un mensaje con información detallada
 * @param {string} mensaje - Texto con el detalle
 */
function detalle(mensaje) {
    const fecha = obtenerFechaHora();
    console.log(`${COLORES.detalle}🔍 [${fecha}] ${mensaje}${COLORES.reset}`);
}

/**
 * Muestra una línea separadora para organizar los mensajes
 * @param {string} [titulo=''] - Texto opcional que se mostrará en el centro
 */
function separador(titulo = '') {
    const linea = '='.repeat(70);
    
    if (titulo) {
        const espacios = ' '.repeat(Math.floor((70 - titulo.length) / 2));
        console.log(`\n${COLORES.info}${espacios}${titulo}${COLORES.reset}`);
        console.log(`${COLORES.info}${linea}${COLORES.reset}\n`);
    } else {
        console.log(`\n${COLORES.info}${linea}${COLORES.reset}\n`);
    }
}

// Exportamos todas las funciones para usarlas en otros archivos
module.exports = {
    exito,
    error,
    aviso,
    info,
    detalle,
    separador
};
