const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicializamos el bot
const bot = new TelegramBot(config.TOKEN, { polling: false });

/**
 * Envía el archivo AL CANAL PRIVADO, mostrando que es de tu canal
 * @param {string} rutaArchivo - Ruta del archivo de vídeo
 * @param {string} mensaje - Texto que acompaña al vídeo
 * @returns {Promise<boolean>} Resultado del envío
 */
async function despacharATelegram(rutaArchivo, mensaje) {
    // Verificamos que el archivo exista
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe, no se puede enviar");
        return false;
    }

    console.log(`📤 Enviando contenido al canal privado...`);

    // Intentamos enviar hasta la cantidad de veces configurada
    let enviadoCorrectamente = false;
    for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
        try {
            // 📤 Solo enviamos al canal privado
            await bot.sendVideo(
                config.CANAL_PRIVADO.ID,
                fs.createReadStream(rutaArchivo),
                {
                    caption: mensaje, // El mensaje muestra que es de tu canal
                    parse_mode: 'HTML'
                },
                {
                    contentType: 'video/mp4',
                    timeout: config.TIMEOUT_SEND
                }
            );

            console.log(`✅ Contenido guardado correctamente en el canal privado`);
            enviadoCorrectamente = true;
            break; // Si salió bien, terminamos

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${config.MAX_RETRIES} fallido: ${error.message}`);
            // Si no es el último intento, esperamos un poco antes de volver a probar
            if (intento < config.MAX_RETRIES) {
                await new Promise(resolve => setTimeout(resolve, 2000));
            }
        }
    }

    if (!enviadoCorrectamente) {
        console.error(`❌ No se pudo guardar el contenido en el canal privado después de ${config.MAX_RETRIES} intentos`);
    }

    return enviadoCorrectamente;
}

module.exports = { despacharATelegram };
