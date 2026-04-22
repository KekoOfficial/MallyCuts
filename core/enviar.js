const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicialización del bot
const bot = new TelegramBot(config.TOKEN, { polling: false });

/**
 * Envía un mismo archivo a los DOS CANALES
 * @param {string} rutaArchivo - Ruta del archivo a enviar
 * @param {string} mensaje - Mensaje que acompaña al vídeo
 * @param {number} numeroParte - Número de la parte que se está enviando
 * @returns {Promise<boolean>} Resultado del proceso
 */
async function enviarADosCanales(rutaArchivo, mensaje, numeroParte) {
    if (!fs.existsSync(rutaArchivo)) {
        console.error(`❌ Parte ${numeroParte}: El archivo no existe`);
        return false;
    }

    console.log(`\n📤 ENVIANDO PARTE ${numeroParte} A LOS DOS CANALES...`);
    let enviadoBien = true;

    // ⚠️ PRIMERO ENVÍO AL CANAL PÚBLICO
    try {
        console.log(`➡️ Enviando a Canal Público: ${config.CANAL_PUBLICO.NOMBRE}`);
        await bot.sendVideo(
            config.CANAL_PUBLICO.ID,
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
        console.log(`✅ Parte ${numeroParte} enviada correctamente a CANAL PÚBLICO`);
    } catch (error) {
        console.error(`❌ Parte ${numeroParte} - Error en Canal Público: ${error.response?.body?.description || error.message}`);
        enviadoBien = false;
    }

    // ⚠️ SEGUNDO ENVÍO AL CANAL PRIVADO
    try {
        console.log(`➡️ Enviando a Canal Privado: ${config.CANAL_PRIVADO.ID}`);
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
        console.log(`✅ Parte ${numeroParte} enviada correctamente a CANAL PRIVADO`);
    } catch (error) {
        console.error(`❌ Parte ${numeroParte} - Error en Canal Privado: ${error.response?.body?.description || error.message}`);
        enviadoBien = false;
    }

    // Resultado final de esta parte
    if (enviadoBien) {
        console.log(`🎉 PARTE ${numeroParte} COMPLETADA EN AMBOS CANALES`);
    } else {
        console.log(`⚠️ PARTE ${numeroParte} TUVO ERRORES EN UNO O AMBOS CANALES`);
    }

    return enviadoBien;
}

module.exports = { enviarADosCanales };
