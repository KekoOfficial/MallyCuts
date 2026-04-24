// 📤 MÓDULO DE ENVÍO A TELEGRAM
// Envía los archivos de video y mensajes a los canales configurados

const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const log = require('../js/logger');
const config = require('../config');

// URL base de la API de Telegram
const API_TELEGRAM_BASE = `https://api.telegram.org/bot${config.TOKEN_BOT}/`;

/**
 * Envía un archivo de video y su mensaje a un canal específico
 * @param {string} rutaArchivo - Ruta completa del archivo a enviar
 * @param {string} mensaje - Texto que acompañará al video
 * @param {string} idCanal - ID o nombre de usuario del canal
 * @param {number} numeroParte - Número de la parte que se está enviando
 * @returns {Promise<boolean>} true si se envió correctamente, false si hubo error
 */
async function enviarACanal(rutaArchivo, mensaje, idCanal, numeroParte) {
    try {
        // Verificamos que el archivo exista
        if (!fs.existsSync(rutaArchivo)) {
            throw new Error(`El archivo no existe: ${rutaArchivo}`);
        }

        const tamanoArchivo = fs.statSync(rutaArchivo).size;
        const tamanoMB = (tamanoArchivo / (1024 * 1024)).toFixed(2);

        log.detalle(`Enviando parte ${numeroParte} al canal ${idCanal} | Tamaño: ${tamanoMB} MB`);

        // Preparamos los datos para enviar
        const formData = new FormData();
        formData.append('chat_id', idCanal);
        formData.append('caption', mensaje);
        formData.append('parse_mode', 'HTML');
        formData.append('supports_streaming', 'true');
        formData.append('video', fs.createReadStream(rutaArchivo), {
            filename: path.basename(rutaArchivo),
            contentType: 'video/mp4'
        });

        // Enviamos la petición a la API de Telegram
        const respuesta = await axios.post(`${API_TELEGRAM_BASE}sendVideo`, formData, {
            headers: formData.getHeaders(),
            maxBodyLength: Infinity,
            maxContentLength: Infinity,
            timeout: 300000 // 5 minutos de tiempo máximo de espera
        });

        // Verificamos la respuesta
        if (respuesta.data && respuesta.data.ok) {
            log.detalle(`✅ Parte ${numeroParte} enviada correctamente a ${idCanal}`);
            return true;
        } else {
            throw new Error(`Respuesta de Telegram: ${JSON.stringify(respuesta.data)}`);
        }

    } catch (error) {
        log.error(`❌ Error al enviar parte ${numeroParte} a ${idCanal}`, error);
        return false;
    }
}

/**
 * Envía el contenido a los dos canales configurados
 * @param {string} rutaArchivo - Ruta completa del archivo a enviar
 * @param {string} mensaje - Texto que acompañará al video
 * @param {number} numeroParte - Número de la parte que se está enviando
 * @returns {Promise<boolean>} true si se envió a al menos un canal, false si fallaron todos
 */
async function enviarADosCanales(rutaArchivo, mensaje, numeroParte) {
    try {
        // Verificamos que tengamos los datos de configuración
        if (!config.TOKEN_BOT) {
            throw new Error('No se configuró el token del bot de Telegram');
        }
        if (!config.CANAL_PRINCIPAL && !config.CANAL_SECUNDARIO) {
            throw new Error('No se configuraron los canales de destino');
        }

        let enviosExitosos = 0;

        // Enviamos al canal principal si está configurado
        if (config.CANAL_PRINCIPAL) {
            const enviado = await enviarACanal(rutaArchivo, mensaje, config.CANAL_PRINCIPAL, numeroParte);
            if (enviado) enviosExitosos++;
        }

        // Enviamos al canal secundario si está configurado
        if (config.CANAL_SECUNDARIO) {
            const enviado = await enviarACanal(rutaArchivo, mensaje, config.CANAL_SECUNDARIO, numeroParte);
            if (enviado) enviosExitosos++;
        }

        // Devolvemos true si al menos se envió a un canal
        return enviosExitosos > 0;

    } catch (error) {
        log.error(`Error general al enviar la parte ${numeroParte}`, error);
        return false;
    }
}

module.exports = {
    enviarADosCanales
};
