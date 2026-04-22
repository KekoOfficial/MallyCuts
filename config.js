// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",
    // 📢 Lista de canales a los que se enviará el contenido (agregá o quitá los que quieras)
    CHAT_IDS: [
        "-1003983527231",
        "-1003706372741"
    ],

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,        // Duración de cada parte en segundos
    MAX_RETRIES: 3,           // Intentos de reenvío si falla
    TIMEOUT_SEND: 300000,    // Tiempo máximo de espera al enviar (5 minutos)

    // 📂 RUTAS DE ARCHIVOS
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
