const TelegramBot = require('node-telegram-bot-api');
const log = require('./logger');
const config = require('../routes/config');
const { generarDescripcion } = require('../routes/titulo');

const bot = new TelegramBot(config.TOKEN, {polling: false});

async function enviarVideo(ruta, titulo, parte, total) {
    const txt = generarDescripcion(titulo, parte, total);
    await bot.sendVideo(config.CANAL_PUBLICO.ID, ruta, {caption: txt.PUBLICO, parse_mode: 'Markdown'});
    log.exito(`✅ Enviado ${parte}/${total}`);
}

module.exports = { enviarVideo };
