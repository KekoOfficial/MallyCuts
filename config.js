// 🤖 BOT DE TELEGRAM
module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 CONFIGURACIÓN DE CANALES
    CANAL_MIO: {
        ID: "-1003983527231",       // Tu canal: solo se muestra en el mensaje
        NOMBRE: "@MallyUmbrae"      // Nombre o enlace que aparecerá en los mensajes
    },
    CANAL_PRIVADO: {
        ID: "-1003706372741"        // Canal privado: AQUÍ SE GUARDAN LOS ARCHIVOS
    },

    // ⚙️ AJUSTES GENERALES
    CLIP_DURATION: 60,        // Duración de cada parte en segundos
    MAX_RETRIES: 3,           // Cantidad de intentos si falla
    TIMEOUT_SEND: 300000,     // Tiempo máximo de espera al enviar (5 minutos)
    TAMANIO_MAXIMO: 50 * 1024 * 1024, // 50MB límite por archivo (límite de Telegram)

    // 📂 Rutas de carpetas
    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
