module.exports = {
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    CANAL_PUBLICO: {
        ID: "-1003983527231",
        NOMBRE: "EnseñaEn15"
    },

    CANAL_PRIVADO: {
        ID: "-1003706372741"
    },

    CLIP_DURATION: 60,
    MAX_RETRIES: 3,
    TIMEOUT_SEND: 300000,
    TAMANIO_MAXIMO: 50 * 1024 * 1024,

    TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output')
};
