// ==============================================
// 📤 MÓDULO DE ENVÍO - MODO DIOS 2.0
// ==============================================

const TelegramBot = require('node-telegram-bot-api');
const log = require('../js/logger');
const config = require('./config');
const { generarDescripcion } = require('./titulo');

// ==============================================
// 🤖 INICIALIZAR BOT
// ==============================================
const bot = new TelegramBot(config.TOKEN, { 
    polling: false,
    baseApiUrl: 'https://api.telegram.org'
});

log.info('🤖 Bot de Telegram listo y conectado');

// ==============================================
// 💤 FUNCIÓN DORMIR
// ==============================================
const dormir = ms => new Promise(resolve => setTimeout(resolve, ms));

// ==============================================
// 🚀 FUNCIÓN PRINCIPAL DE ENVÍO
// ==============================================
async function enviarVideo(rutaArchivo, titulo, numeroParte = 1, totalPartes = 1) {
    
    // 🎬 OBTENER TEXTO FORMATEADO PERFECTO
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
    await bot.sendVideo(config.CANAL_PUBLICO.ID, rutaArchivo, opciones);
    log.exito(`✅ ENVIADO: Parte ${numeroParte}`);

    // ==============================================
    // 📂 ENVIAR TAMBIÉN AL CANAL PRIVADO (RESPALDO)
    // ==============================================
    if(config.CANAL_PRIVADO && config.CANAL_PRIVADO.ID) {
        try {
            await bot.sendVideo(config.CANAL_PRIVADO.ID, rutaArchivo, {
                caption: textos.PRIVADO
            });
        } catch (err) {
            log.warn('⚠️ Respaldo no disponible o falló');
        }
    }

    return true;
}

// ==============================================
// 📢 FUNCIÓN ENVIAR MENSAJE DE TEXTO
// ==============================================
async function enviarMensaje(texto, canal = 'PUBLICO') {
    try {
        const chatId = canal === 'PUBLICO' ? config.CANAL_PUBLICO.ID : config.CANAL_PRIVADO.ID;
        
        await bot.sendMessage(chatId, texto, {
            parse_mode: 'Markdown'
        });
        return true;
    } catch (err) {
        log.error('❌ Error al enviar mensaje', err);
        return false;
    }
}

module.exports = { 
    enviarVideo, 
    enviarMensaje 
};
