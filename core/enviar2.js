// enviar2.js
const FormData = require('form-data'); // Instala esto: npm install form-data
const fs = require('fs');
const axios = require('axios'); // Instala esto: npm install axios

// Función para enviar una parte por separado
async function enviarParte(rutaArchivo, nombreParte) {
    const intentosMaximos = 3;

    for (let intento = 1; intento <= intentosMaximos; intento++) {
        try {
            console.log(`📤 Enviando ${nombreParte} al canal privado...`);

            // Creamos el cuerpo de la solicitud y AGREGAMOS EL ARCHIVO CORRECTAMENTE
            const datosEnvio = new FormData();
            datosEnvio.append('video', fs.createReadStream(rutaArchivo)); // ¡ESTO ES LO QUE FALTABA!
            datosEnvio.append('descripcion', `${nombreParte} del archivo`);
            // Agrega aquí cualquier otro dato que necesites enviar

            // Hacemos la solicitud
            await axios.post('URL_DE_TU_API_O_SERVICIO', datosEnvio, {
                headers: datosEnvio.getHeaders()
            });

            console.log(`✅ ${nombreParte} enviada correctamente en el intento ${intento}`);
            return; // Salimos si se envió bien

        } catch (error) {
            console.log(`⚠️ Intento ${intento}/${intentosMaximos} fallido`);
            console.log(`ℹ️ Motivo: ${error.response?.data?.message || error.message}`);

            // Si ya son todos los intentos, lanzamos el error
            if (intento === intentosMaximos) {
                throw new Error(`No se pudo enviar ${nombreParte} después de ${intentosMaximos} intentos`);
            }

            // Esperamos un poco antes de volver a intentar
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
}

// Exportamos la función para usarla en otros archivos
module.exports = { enviarParte };
