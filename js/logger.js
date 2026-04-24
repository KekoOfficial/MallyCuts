// ==============================================
// 📋 LOGGER AVANZADO - MALLYCUTS
// ==============================================

// Códigos de color para la consola
const colores = {
    reset: "\x1b[0m",
    rojo: "\x1b[31m",
    verde: "\x1b[32m",
    amarillo: "\x1b[33m",
    azul: "\x1b[34m",
    magenta: "\x1b[35m",
    cian: "\x1b[36m",
    blanco: "\x1b[37m",
    gris: "\x1b[90m"
};

// Formatear fecha actual (SIN INSTALAR NADA)
function obtenerFecha() {
    const ahora = new Date();
    
    const dia = String(ahora.getDate()).padStart(2, '0');
    const mes = String(ahora.getMonth() + 1).padStart(2, '0');
    const anio = ahora.getFullYear();
    
    let horas = ahora.getHours();
    const minutos = String(ahora.getMinutes()).padStart(2, '0');
    const segundos = String(ahora.getSeconds()).padStart(2, '0');
    
    const ampm = horas >= 12 ? 'p. m.' : 'a. m.';
    horas = horas % 12 || 12; // Convertir a formato 12h

    return `${dia}/${mes}/${anio}, ${horas}:${minutos}:${segundos} ${ampm}`;
}

// ==============================================
// 📝 FUNCIONES DE LOG
// ==============================================

const log = {
    // Separador visual
    separador: function() {
        console.log(colores.cian + "=".repeat(60) + colores.reset);
    },

    // ✅ Éxito / Correcto
    exito: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.verde}[${fecha}] ✅ ${mensaje}${colores.reset}`);
    },

    // ℹ️ Información normal
    info: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.blanco}[${fecha}] ℹ️  ${mensaje}${colores.reset}`);
    },

    // 🔍 Detalle / Progreso
    detalle: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.gris}[${fecha}] 🔍 ${mensaje}${colores.reset}`);
    },

    // ⚠️ Aviso / Atención
    aviso: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.amarillo}[${fecha}] ⚠️  ${mensaje}${colores.reset}`);
    },

    // ❌ Error
    error: function(mensaje, error = null) {
        const fecha = obtenerFecha();
        console.log(`${colores.rojo}[${fecha}] ❌ ${mensaje}${colores.reset}`);
        if (error && error.stack) {
            console.log(colores.rojo + "📄 Detalle técnico:" + colores.reset);
            console.log(error.stack);
        }
    },

    // 🚀 Proceso iniciando
    inicio: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.magenta}[${fecha}] 🚀 ${mensaje}${colores.reset}`);
    },

    // 📊 Datos o estadísticas
    dato: function(mensaje) {
        const fecha = obtenerFecha();
        console.log(`${colores.azul}[${fecha}] 📊 ${mensaje}${colores.reset}`);
    }
};

module.exports = log;
