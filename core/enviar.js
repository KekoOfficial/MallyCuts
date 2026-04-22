const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicializar bot
const bot = new TelegramBot(config.TOKEN, { polling: false });

// 📤 ENVIAR ARCHIVO A TELEGRAM
function despacharATelegram(rutaArchivo, mensaje) {
    return new Promise(async (resolve) => {
        for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
            try {
                if (!fs.existsSync(rutaArchivo)) {
                    console.error(`❌ Archivo no encontrado: ${rutaArchivo}`);
                    return resolve(false);
                }

                // Enviar vídeo
                await bot.sendVideo(
                    config.CHAT_ID,
                    fs.createReadStream(rutaArchivo),
                    {
                        caption: mensaje,
                        parse_mode: 'HTML',
                        timeout: config.TIMEOUT_SEND,
                        supports_streaming: true
                    }
                );

                resolve(true);
                break;

            } catch (error) {
                const mensajeError = error.message || '';
                
                // Manejar error de archivo muy grande
                if (mensajeError.includes('413') || mensajeError.includes('Too Large')) {
                    console.warn(`⚠️ Archivo pesado, reintentando...`);
                }

                console.warn(`⚠️ Intento ${intento} fallido: ${mensajeError}`);

                // Esperar antes de reintentar
                if (intento < config.MAX_RETRIES) {
                    await new Promise(resolve => setTimeout(resolve, 5000));
                } else {
                    resolve(false);
                }
            }
        }
    });
}

module.exports = { despacharATelegram };
