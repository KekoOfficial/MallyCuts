// 🤖 CONFIGURACIÓN DEL BOT Y CANALES
module.exports = {
    // TU TOKEN DEL BOT
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 CANAL PÚBLICO (Lo que ven todos, tu marca)
    CANAL_PUBLICO: {
        ID: "-1003983527231",
        NOMBRE: "EnseñaEn15"
    },

    // 🔒 CANAL PRIVADO (Solo vos, donde se guardan los archivos)
    CANAL_PRIVADO: {
        ID: "-1003706372741"
    },

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,        // Duración de cada parte en segundos
    MAX_RETRIES: 3,           // Intentos si falla el envío
    TIMEOUT_SEND: 300000,     // Tiempo máximo de espera por envío
    TAMANIO_MAXIMO: 50 * 1024 * 1024, // Límite de Telegram: 50MB por archivo

    // 📂 CARPETAS DE TRABAJO
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
