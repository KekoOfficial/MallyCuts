const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

const bot = new TelegramBot(config.TOKEN, { 
    polling: false,
    filepath: false
});

// Función de envío separada
async function enviarSegundoContenido(rutaArchivo, mensaje) {
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe para enviar por el segundo método");
        return false;
    }

    console.log(`📤 Enviando por el segundo método...`);
    let enviado = false;

    for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
        try {
            await bot.sendVideo(
                config.CANAL_PRIVADO.ID,
                fs.createReadStream(rutaArchivo),
                {
                    caption: mensaje + " (Enviado por método 2)",
                    parse_mode: 'HTML'
                },
                {
                    contentType: 'video/mp4',
                    timeout: config.TIMEOUT_SEND
                }
            );

            console.log(`✅ Enviado correctamente por el segundo método`);
            enviado = true;
            break;

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${config.MAX_RETRIES} fallido en método 2`);
            console.error(`ℹ️ Motivo: ${error.response?.body?.description || error.message}`);
            if (intento < config.MAX_RETRIES) await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    return enviado;
}

module.exports = { enviarSegundoContenido };
