// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 CONFIGURACIÓN DE CANALES
    CANAL_MIO: {
        ID: "-1003983527231",       // Tu canal, solo se muestra en el mensaje
        NOMBRE: "@MallyUmbrae"      // Nombre que aparece
    },
    CANAL_PRIVADO: {
        ID: "-1003706372741"        // Canal privado, AQUÍ SE GUARDA EL ARCHIVO
    },

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,        // Duración de cada parte
    MAX_RETRIES: 3,           // Intentos si falla
    TIMEOUT_SEND: 300000,     // Tiempo de espera
    TAMANIO_MAXIMO: 50 * 1024 * 1024,

    // 📂 Rutas
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
