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
     TEMP_FOLDER: require('path').join(__dirname, 'videos', 'output'), // Donde se guardan las partes generadas
     ORIGINAL_FOLDER: require('path').join(__dirname, 'videos', 'originales'), // 🆕 Donde se guardan los videos descargados
     INPUT_FOLDER: require('path').join(__dirname, 'videos', 'input'), // 🆕 Carpeta de entrada para archivos subidos
     TEMP_UPLOAD_FOLDER: require('path').join(__dirname, 'temp_uploads'), // 🆕 Carpeta temporal para subidas
     // ⚙️ AJUSTES NUEVOS PARA EL SISTEMA DE DESCARGA AUTOMÁTICA
     BORRAR_ARCHIVOS_DESPUES: true, // Poné en false si querés guardar todos los archivos descargados y generados
     VELOCIDAD_PREDETERMINADA: 1.3, // Velocidad que se usará automáticamente en todos los videos
     TEXTO_MARCA_PREDETERMINADA: "EnseñaEn15" // Tu marca que se agregará a todos los videos
 };
 // 🛠️ CREAMOS TODAS LAS CARPETAS AUTOMÁTICAMENTE SI NO EXISTEN
 const fs = require('fs');
 const carpetas = [
     module.exports.TEMP_FOLDER,
     module.exports.ORIGINAL_FOLDER,
     module.exports.INPUT_FOLDER,
     module.exports.TEMP_UPLOAD_FOLDER
 ];
 carpetas.forEach(ruta => {
     if (!fs.existsSync(ruta)) {
         fs.mkdirSync(ruta, { recursive: true });
         console.log(`📂 Carpeta creada: ${ruta}`);
     }
 });