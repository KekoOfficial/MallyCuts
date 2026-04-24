// 🤖 CONFIGURACIÓN DEL BOT Y CANALES
// Acá se definen todos los parámetros de funcionamiento del sistema

// Importamos módulos necesarios
const fs = require('fs');
const path = require('path');

module.exports = {
    // 🗝️ TU TOKEN DEL BOT DE TELEGRAM
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 CANAL PÚBLICO (Lo que ven todos, tu marca)
    CANAL_PUBLICO: {
        ID: "-1003983527231",
        NOMBRE: "EnseñaEn15"
    },

    // 🔒 CANAL PRIVADO (Solo acceso tuyo, donde se guardan los archivos)
    CANAL_PRIVADO: {
        ID: "-1003706372741"
    },

    // ⚙️ AJUSTES GENERALES DE PROCESAMIENTO
    CLIP_DURATION: 60,        // Duración de cada parte del video, expresada en segundos
    MAX_RETRIES: 3,           // Cantidad máxima de intentos si falla el envío de un archivo
    TIMEOUT_SEND: 300000,     // Tiempo máximo de espera por cada operación de envío (5 minutos)
    TAMANIO_MAXIMO: 50 * 1024 * 1024, // Límite permitido por la API de Telegram: 50MB por archivo

    // 📂 RUTAS DE CARPETAS DE TRABAJO
    TEMP_FOLDER: path.join(__dirname, 'videos', 'output'),          // Donde se guardan temporalmente las partes generadas
    ORIGINAL_FOLDER: path.join(__dirname, 'videos', 'originales'),   // Donde se guardan los videos descargados o subidos
    INPUT_FOLDER: path.join(__dirname, 'videos', 'input'),          // Carpeta de entrada para los archivos que se suben manualmente
    TEMP_UPLOAD_FOLDER: path.join(__dirname, 'temp_uploads'),        // Carpeta temporal usada durante el proceso de subida

    // ⚙️ AJUSTES ADICIONALES DEL SISTEMA
    BORRAR_ARCHIVOS_DESPUES: true,    // Poné en false si querés conservar todos los archivos después de procesarlos
    VELOCIDAD_PREDETERMINADA: 1.3,    // Velocidad de reproducción que se aplicará automáticamente a todos los videos
    TEXTO_MARCA_PREDETERMINADA: "EnseñaEn15" // Nombre de tu marca que se agregará a los mensajes y archivos
};

// 🛠️ CREAMOS TODAS LAS CARPETAS AUTOMÁTICAMENTE SI NO EXISTEN
const carpetas = [
    module.exports.TEMP_FOLDER,
    module.exports.ORIGINAL_FOLDER,
    module.exports.INPUT_FOLDER,
    module.exports.TEMP_UPLOAD_FOLDER
];

carpetas.forEach(rutaCarpeta => {
    try {
        if (!fs.existsSync(rutaCarpeta)) {
            fs.mkdirSync(rutaCarpeta, { recursive: true, mode: 0o777 });
            console.log(`📂 Carpeta creada correctamente: ${rutaCarpeta}`);
        } else {
            console.log(`✅ Carpeta ya disponible: ${rutaCarpeta}`);
        }
    } catch (error) {
        console.error(`❌ Error al crear o acceder a la carpeta: ${rutaCarpeta}`, error.message);
    }
});
