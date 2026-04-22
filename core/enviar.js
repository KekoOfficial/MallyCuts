const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

// Inicializamos el bot
const bot = new TelegramBot(config.TOKEN, { 
    polling: false,
    filepath: false // Configuración para evitar el aviso que te aparecía
});

/**
 * Envía el archivo AL CANAL PRIVADO, mostrando los datos de tu canal
 * @param {string} rutaArchivo - Ruta del archivo de vídeo
 * @param {string} mensaje - Texto que acompaña al archivo
 * @returns {Promise<boolean>} Resultado de la operación
 */
async function despacharATelegram(rutaArchivo, mensaje) {
    // 🛡️ Validaciones previas
    if (!fs.existsSync(rutaArchivo)) {
        console.error("❌ El archivo no existe, no se puede enviar");
        return false;
    }

    if (!config.CANAL_PRIVADO.ID || !config.CANAL_PRIVADO.ID.startsWith("-100")) {
        console.error("❌ El ID del canal privado es incorrecto o está vacío");
        return false;
    }

    // Verificamos tamaño del archivo
    const tamañoArchivo = fs.statSync(rutaArchivo).size;
    if (tamañoArchivo > config.TAMANIO_MAXIMO) {
        console.error(`❌ El archivo pesa ${Math.round(tamañoArchivo/1024/1024)}MB, supera el límite de 50MB permitido por Telegram`);
        return false;
    }

    console.log(`📤 Enviando contenido al canal privado...`);
    let enviadoCorrectamente = false;

    // Intentos de envío
    for (let intento = 1; intento <= config.MAX_RETRIES; intento++) {
        try {
            // ✅ Método actualizado y recomendado, sin avisos de advertencia
            await bot.sendVideo(
                config.CANAL_PRIVADO.ID,
                { source: rutaArchivo },
                {
                    caption: mensaje,
                    parse_mode: 'HTML'
                },
                {
                    timeout: config.TIMEOUT_SEND
                }
            );

            console.log(`✅ ¡ENVIADO CORRECTAMENTE! Todo guardado en tu canal privado`);
            enviadoCorrectamente = true;
            break;

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${config.MAX_RETRIES} fallido`);
            
            // 📌 Mensajes de error detallados para saber qué pasa
            if (error.response?.body?.description === "Bad Request: chat not found") {
                console.error("❌ No se encuentra el canal. Asegurate de:");
                console.error("   1. El ID del canal es correcto");
                console.error("   2. Agregaste el bot como administrador del canal");
                console.error("   3. El canal no fue eliminado o cambiado de nombre");
                break; // Si el canal no existe, no tiene sentido seguir intentando
            } else {
                console.error(`ℹ️ Motivo: ${error.response?.body?.description || error.message}`);
                if (intento < config.MAX_RETRIES) {
                    await new Promise(resolve => setTimeout(resolve, 3000)); // Esperamos 3 segundos antes de volver a intentar
                }
            }
        }
    }

    return enviadoCorrectamente;
}

module.exports = { despacharATelegram };
