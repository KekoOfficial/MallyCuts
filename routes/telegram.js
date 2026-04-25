// ==============================================
// 📤 MÓDULO TELEGRAM - MALLYCUTS
// ==============================================

const TelegramBot = require('node-telegram-bot-api');
const log = require('../js/logger');
const config = require('../config');

// ✅ IMPORTAR NUEVO MÓDULO DE TÍTULOS
const { generarDescripcion } = require('./titulo');

// ==============================================
// 🤖 INICIALIZAR BOT
// ==============================================

const bot = new TelegramBot(config.TOKEN, { 
    polling: false,
    baseApiUrl: 'https://api.telegram.org'
});

log.info('🤖 Bot de Telegram conectado y listo');
log.dato(`📢 Canal Público: ${config.CANAL_PUBLICO.NOMBRE}`);

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL ENVIAR VIDEO
// ==============================================

async function enviarVideo(rutaArchivo, titulo, numeroParte = 1, totalPartes = 1) {
    
    return new Promise((resolve, reject) => {
        
        log.info(`📤 Iniciando envío: ${titulo} (Parte ${numeroParte})`);

        // 🎬 OBTENER TEXTOS FORMATEADOS
        const textos = generarDescripcion(titulo, numeroParte, totalPartes);

        const opciones = {
            caption: textos.PUBLICO,
            parse_mode: 'Markdown',
            supports_streaming: true,
            disable_notification: false
        };

        // ==============================================
        // 📤 ENVIAR AL CANAL PÚBLICO
        // ==============================================
        bot.sendVideo(config.CANAL_PUBLICO.ID, rutaArchivo, opciones)
            .then(() => {
                log.exito(`✅ ENVIADO AL CANAL: ${titulo}`);
                
                // ==============================================
                // 📥 ENVIAR TAMBIÉN AL CANAL PRIVADO
                // ==============================================
                if(config.CANAL_PRIVADO && config.CANAL_PRIVADO.ID) {
                    bot.sendVideo(config.CANAL_PRIVADO.ID, rutaArchivo, {
                        caption: textos.PRIVADO
                    }).catch(err => log.warn('Respaldar:', err));
                }

                resolve(true);

            })
            .catch((err) => {
                log.error(`❌ FALLO ENVIO: ${titulo}`, err);
                reject(err);
            });
    });
}

// ==============================================
// 📢 FUNCIÓN ENVIAR MENSAJE RÁPIDO
// ==============================================

async function enviarMensaje(texto, canal = 'PUBLICO') {
    try {
        const chatId = canal === 'PUBLICO' ? config.CANAL_PUBLICO.ID : config.CANAL_PRIVADO.ID;
        
        await bot.sendMessage(chatId, texto, {
            parse_mode: 'Markdown'
        });
        return true;
    } catch (err) {
        log.error('Error mensaje:', err);
        return false;
    }
}

module.exports = { 
    enviarVideo, 
    enviarMensaje 
};
