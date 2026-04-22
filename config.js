// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU",
    CHAT_ID: "-1003584710096",

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,       // Duración de cada parte en segundos
    MAX_RETRIES: 3,          // Intentos de reenvío si falla
    TIMEOUT_SEND: 300000,    // Tiempo máximo de espera al enviar (5 minutos)

    // 📂 RUTAS DE ARCHIVOS
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
