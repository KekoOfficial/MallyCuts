const fs = require('fs');
const axios = require('axios');
const config = require('../config');

/**
 * Envía un video y su mensaje a los DOS canales automáticamente
 * @param {string} rutaArchivo - Ruta del archivo de video a enviar
 * @param {string} mensaje - Texto que irá junto al video
 * @param {number} numeroParte - Número de la parte que se está enviando
 * @returns {Promise<boolean>} Resultado del envío
 */
async function enviarADosCanales(rutaArchivo, mensaje, numeroParte) {
    try {
        console.log(`📤 Enviando parte ${numeroParte} a los canales...`);

        // Primero enviamos al CANAL PÚBLICO
        await enviarVideoACanal(config.CANAL_PUBLICO.ID, mensaje, rutaArchivo);
        console.log(`✅ Parte ${numeroParte} enviada al canal público`);

        // Pequeña pausa para no saturar
        await new Promise(resolve => setTimeout(resolve, 800));

        // Después enviamos al CANAL PRIVADO
        await enviarVideoACanal(config.CANAL_PRIVADO.ID, mensaje, rutaArchivo);
        console.log(`✅ Parte ${numeroParte} enviada al canal privado`);

        return true;

    } catch (error) {
        console.error(`❌ Error al enviar parte ${numeroParte}:`, error.message);
        return false;
    }
}

/**
 * Función auxiliar que hace el envío real a un canal específico
 * @param {string} idCanal - ID del canal o grupo
 * @param {string} texto - Mensaje a enviar
 * @param {string} rutaArchivo - Ruta del archivo
 */
async function enviarVideoACanal(idCanal, texto, rutaArchivo) {
    // Verificamos que el archivo exista
    if (!fs.existsSync(rutaArchivo)) {
        throw new Error("El archivo no existe: " + rutaArchivo);
    }

    // Verificamos el tamaño (máximo 50MB según la configuración)
    const tamañoArchivo = fs.statSync(rutaArchivo).size;
    if (tamañoArchivo > config.TAMANIO_MAXIMO) {
        throw new Error(`El archivo es demasiado grande (${(tamañoArchivo / 1024 / 1024).toFixed(2)}MB), límite: 50MB`);
    }

    // Datos para el envío
    const formData = new FormData();
    formData.append('chat_id', idCanal);
    formData.append('caption', texto);
    formData.append('parse_mode', 'HTML');
    formData.append('video', fs.createReadStream(rutaArchivo));

    // Enviamos usando la API de Telegram
    await axios.post(
        `https://api.telegram.org/bot${config.TOKEN}/sendVideo`,
        formData,
        {
            headers: formData.getHeaders(),
            timeout: config.TIMEOUT_SEND
        }
    );
}

module.exports = { enviarADosCanales };
