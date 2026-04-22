const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const config = require('../config');

const bot = new TelegramBot(config.TOKEN, { polling: false });

async function enviarADosCanales(rutaArchivo, mensaje, numeroParte) {
    if (!fs.existsSync(rutaArchivo)) {
        console.error(`❌ Parte ${numeroParte}: El archivo no existe`);
        return false;
    }

    console.log(`📤 Procesando envío de la parte ${numeroParte} a los dos canales`);
    let enviadoBien = true;

    // Enviar al canal público
    try {
        console.log(`➡️ Enviando a CANAL PÚBLICO: ${config.CANAL_PUBLICO.NOMBRE}`);
        await bot.sendVideo(
            config.CANAL_PUBLICO.ID,
            fs.createReadStream(rutaArchivo),
