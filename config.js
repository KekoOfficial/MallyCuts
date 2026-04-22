// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 CONFIGURACIÓN DE CANALES
    CANAL_MIO: {
        ID: "-1003983527231",       // Este es tu canal, aparecerá en el mensaje
        NOMBRE: "@MallyUmbrae"      // Poné el nombre o enlace que quieras que se muestre
    },
    CANAL_PRIVADO: {
        ID: "-1003706372741"        // Este es el canal privado, AQUÍ SE GUARDARÁN LOS ARCHIVOS
    },

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,        // Duración de cada parte en segundos
    MAX_RETRIES: 3,           // Cantidad de intentos si falla
    TIMEOUT_SEND: 300000,    // Tiempo de espera máximo al enviar (5 minutos)

    // 📂 Rutas de carpetas
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
