// 📤 MÓDULO DE ENVÍO A TELEGRAM
// Adaptado para la nueva estructura de configuración

const fs = require('fs');
const path = require('path');
const axios = require('axios');
const FormData = require('form-data');
const log = require('../js/logger');
const config = require('../config');

// URL base de la API
const API_URL = `https://api.telegram.org/bot${config.TOKEN}/`;

/**
 * Envía un video a un canal específico
 */
async function enviarACanal(rutaArchivo, mensaje, idCanal, numeroParte) {
    try {
        if (!fs.existsSync(rutaArchivo)) {
            throw new Error(`Archivo no encontrado: ${rutaArchivo}`);
        }

        const tamanoMB = (fs.statSync(rutaArchivo).size / (1024 * 1024)).toFixed(2);
        log.detalle(`Enviando parte ${numeroParte} al canal ${idCanal} | ${tamanoMB} MB`);

        // Preparamos datos
        const formData = new FormData();
        formData.append('chat_id', idCanal);
        formData.append('caption', mensaje);
        formData.append('parse_mode', 'HTML');
        formData.append('supports_streaming', 'true');
        formData.append('video', fs.createReadStream(rutaArchivo), {
            filename: path.basename(rutaArchivo),
            contentType: 'video/mp4'
        });

        // Enviamos
        const respuesta = await axios.post(`${API_URL}sendVideo`, formData, {
            headers: formData.getHeaders(),
            maxBodyLength: Infinity,
            timeout: config.TIEMPO_ESPERA_ENVIO || 300000
        });

        if (respuesta.data && respuesta.data.ok) {
            log.exito(`✅ Parte ${numeroParte} enviada correctamente`);
            return true;
        } else {
            throw new Error(`Respuesta API: ${JSON.stringify(respuesta.data)}`);
        }

    } catch (error) {
        log.error(`❌ Error al enviar parte ${numeroParte}`, error);
        return false;
    }
}

/**
 * Envía a los dos canales configurados
 */
async function enviarADosCanales(rutaArchivo, mensaje, numeroParte) {
    try {
        // Verificamos credenciales
        if (!config.TOKEN) {
            throw new Error('No se configuró el TOKEN del bot en config.js');
        }

        const canalPublicoID = config.CANAL_PUBLICO.ID;
        const canalPrivadoID = config.CANAL_PRIVADO.ID;

        if (!canalPublicoID && !canalPrivadoID) {
            throw new Error('No hay canales configurados para enviar');
        }

        let enviadoOK = false;

        // Enviar al canal público
        if (canalPublicoID) {
            const enviado = await enviarACanal(rutaArchivo, mensaje, canalPublicoID, numeroParte);
            if (enviado) enviadoOK = true;
        }

        // Enviar al canal privado
        if (canalPrivadoID) {
            const enviado = await enviarACanal(rutaArchivo, mensaje, canalPrivadoID, numeroParte);
            if (enviado) enviadoOK = true;
        }

        return enviadoOK;

    } catch (error) {
        log.error(`Error general envío parte ${numeroParte}`, error);
        return false;
    }
}

module.exports = {
    enviarADosCanales
};
