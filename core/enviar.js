const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

const bot = new TelegramBot(config.TOKEN, { polling: false });

async function despacharATelegram(rutaArchivo, mensaje) {
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe");
        return false;
    }

    console.log(`📤 Enviando contenido AL CANAL PRIVADO...`);
    let enviadoCorrectamente = false;

    for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
        try {
            // ✅ Se envía SOLO al canal privado, pero el mensaje muestra tu canal público
            await bot.sendVideo(
                config.CANAL_PRIVADO.ID,
                fs.createReadStream(rutaArchivo),
                {
                    caption: mensaje,
                    parse_mode: 'HTML'
                },
                {
                    contentType: 'video/mp4',
                    timeout: config.TIMEOUT_SEND
                }
            );

            console.log(`✅ ¡ENVIADO CORRECTAMENTE! Guardado en canal privado, mensaje muestra: ${config.CANAL_MIO.NOMBRE}`);
            enviadoCorrectamente = true;
            break;

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${config.MAX_RETRIES} fallido`);
            
            if (error.response?.body?.description === "Bad Request: chat not found") {
                console.error("❌ No se encuentra el canal. Verificá que el bot sea administrador.");
                break;
            } else {
                console.error(`ℹ️ Motivo: ${error.response?.body?.description || error.message}`);
                if (intento < config.MAX_RETRIES) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }
    }

    return enviadoCorrectamente;
}

module.exports = { despacharATelegram };
