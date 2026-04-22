// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 LOS DOS CANALES COMO LOS QUERÍAS
    CANAL_MIO: {
        ID: "-1003983527231",       // Tu canal público, solo se muestra en el mensaje
        NOMBRE: "@OliDevX"      // Tu nombre o enlace que aparece para todos
    },
    CANAL_PRIVADO: {
        ID: "-1003706372741"        // Tu canal privado, AQUÍ SE GUARDAN LOS ARCHIVOS
    },

    // ⚙️ AJUSTES
    CLIP_DURATION: 60,        // Duración de cada parte
    MAX_RETRIES: 3,           // Intentos si falla
    TIMEOUT_SEND: 300000,     // Tiempo de espera
    TAMANIO_MAXIMO: 50 * 1024 * 1024,

    // 📂 CARPETAS
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
