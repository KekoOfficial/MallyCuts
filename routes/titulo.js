// ==============================================
// 📛 MÓDULO GENERADOR DE TÍTULOS - MALLYCUTS
// ==============================================

const config = require('../config');

// ==============================================
// 📝 FUNCIÓN PRINCIPAL: CREAR LA DESCRIPCIÓN
// ==============================================

function generarDescripcion(titulo, numeroParte = 1, totalPartes = 1) {
    
    // Emojis disponibles para variar un poco
    const emojis = ['🎬', '🔥', '⚡', '📺', '✨'];
    const emojiAleatorio = emojis[Math.floor(Math.random() * emojis.length)];

    // ==============================================
    // 📢 TEXTO PARA EL CANAL PÚBLICO
    // ==============================================
    const publico = `
${emojiAleatorio} *${titulo}*

📌 Parte ${numeroParte} de ${totalPartes}
⚡ Velocidad: ${config.VELOCIDAD_VIDEO}x
🔥 ${config.TEXTO_MARCA_AGUA}
    `.trim();

    // ==============================================
    // 📂 TEXTO PARA EL CANAL PRIVADO (RESPALDO)
    // ==============================================
    const privado = `🎬: ${titulo} (Parte ${numeroParte})`;

    // ==============================================
    // 📦 DEVOLVER AMBOS TEXTOS
    // ==============================================
    return {
        PUBLICO: publico,
        PRIVADO: privado
    };
}

// ==============================================
// 🧹 FUNCIÓN: LIMPIAR NOMBRE PARA ARCHIVO
// ==============================================

function limpiarNombreParaArchivo(texto) {
    // Quitamos caracteres raros, espacios y símbolos
    return texto
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "") // Quitar tildes
        .replace(/[^a-zA-Z0-9\s]/g, '')   // Quitar símbolos
        .trim()
        .replace(/\s+/g, '_');            // Cambiar espacios por _
}

module.exports = {
    generarDescripcion,
    limpiarNombreParaArchivo
};
