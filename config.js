// 🤖 CONFIGURACIÓN DEL BOT
module.exports = {
    // Poné acá TU TOKEN del bot
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // Poné acá EL ÚNICO ID DE CANAL donde querés que se envíe todo
    CANAL_ID: "-1003983527231",

    // ⚙️ Ajustes básicos
    CLIP_DURATION: 60,        // Duración de cada parte en segundos
    MAX_RETRIES: 3,           // Intentos si falla el envío
    TIMEOUT_SEND: 300000,     // Tiempo máximo de espera al enviar

    // 📂 Carpetas
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
