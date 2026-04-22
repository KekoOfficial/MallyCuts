const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicialización simple
const bot = new TelegramBot(config.TOKEN, { polling: false });

async function despacharATelegram(rutaArchivo, mensaje) {
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe");
        return false;
    }

    console.log(`📤 Enviando contenido al canal...`);
    let enviado = false;

    // Intentos de envío
    for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
        try {
            // Método correcto y probado
            await bot.sendVideo(
                config.CANAL_ID,
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

            console.log(`✅ ¡ENVIADO CORRECTAMENTE!`);
            enviado = true;
            break;

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${config.MAX_RETRIES} fallido`);
            
            if (error.response?.body?.description === "Bad Request: chat not found") {
                console.error("❌ No se encuentra el canal. Verificá:");
                console.error("   - Que el ID sea correcto");
                console.error("   - Que el bot sea administrador del canal");
                break;
            } else {
                console.error(`ℹ️ Motivo: ${error.response?.body?.description || error.message}`);
                if (intento < config.MAX_RETRIES) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
        }
    }

    return enviado;
}

module.exports = { despacharATelegram };
