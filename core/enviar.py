const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicializamos el bot
const bot = new TelegramBot(config.TOKEN, { polling: false });

/**
 * Envía el vídeo a TODOS los canales configurados
 * @param {string} rutaArchivo - Ruta del archivo de vídeo
 * @param {string} mensaje - Texto que irá junto al vídeo
 * @returns {Promise<boolean>} True si se envió a todos, false si hubo errores
 */
async function despacharATelegram(rutaArchivo, mensaje) {
    // Verificamos que el archivo exista
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe para enviar");
        return false;
    }

    let enviadoCorrectamente = true;

    // Recorremos TODOS los canales y enviamos el archivo a cada uno
    for (const chatId of config.CHAT_IDS) {
        console.log(`📤 Enviando al canal: ${chatId}`);

        // Intentamos enviar hasta la cantidad de veces configurada
        for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
            try {
                await bot.sendVideo(chatId, rutaArchivo, {
                    caption: mensaje,
                    parse_mode: 'HTML'
                }, {
                    timeout: config.TIMEOUT_SEND
                });

                console.log(`✅ Enviado exitosamente al canal: ${chatId}`);
                break; // Si salió bien, salimos del ciclo de intentos

            } catch (error) {
                console.error(`⚠️ Error al enviar a ${chatId} (intento ${intento}/${config.MAX_RETRIES}):`, error.message);
                
                // Si es el último intento y falló, marcamos como error
                if (intento === config.MAX_RETRIES) {
                    console.error(`❌ No se pudo enviar al canal: ${chatId}`);
                    enviadoCorrectamente = false;
                } else {
                    // Esperamos un poco antes de volver a intentar
                    await new Promise(resolve => setTimeout(resolve, 3000));
                }
            }
        }
    }

    return enviadoCorrectamente;
}

module.exports = { despacharATelegram };
