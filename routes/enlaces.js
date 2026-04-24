// 🔗 RUTAS Y FUNCIONES PARA PROCESAR ENLACES DE DESCARGA
// Se encarga de recibir el enlace, descargar el video, dividirlo y enviarlo

const express = require('express');
const fs = require('fs');
const router = express.Router();

// Importamos las dependencias y módulos necesarios
const log = require('../js/logger');
const config = require('../config');
const { obtenerDuracionVideo, formatoDuracion, archivoEsValido } = require('./utilidades');
const { procesarEnlace } = require('../core/descargar');
const { extraerSegmento } = require('../core/cortar');
const { enviarADosCanales } = require('../core/enviar');

/**
 * Ruta principal para recibir y procesar solicitudes por enlace
 */
router.post('/procesar-enlace', async (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ENLACE');

    try {
        // Verificamos que se hayan enviado los datos obligatorios
        if (!req.body?.enlace || !req.body?.titulo) {
            log.error('Faltan datos: no se envió el enlace o el título del video');
            return res.json({
                status: 'error',
                mensaje: '❌ Debés ingresar tanto el enlace de descarga como el título del video'
            });
        }

        // Extraemos los datos recibidos
        const { enlace, titulo } = req.body;

        // Mostramos la información recibida en los registros
        log.info('Datos recibidos correctamente:');
        log.detalle(`Enlace: ${enlace}`);
        log.detalle(`Título: ${titulo}`);

        log.aviso('Iniciando proceso de descarga... Esto puede tardar bastante dependiendo del tamaño del archivo y la velocidad de tu conexión a internet');

        // Llamamos al módulo de descarga para obtener el archivo
        const rutaVideoDescargado = await procesarEnlace(enlace, titulo);

        // Verificamos que la descarga haya sido exitosa y el archivo sea válido
        if (!rutaVideoDescargado || !archivoEsValido(rutaVideoDescargado)) {
            log.error('No se pudo descargar el video o el archivo descargado es inválido');
            return res.json({
                status: 'error',
                mensaje: '❌ Falló la descarga del video. Verificá que el enlace sea válido y funcione correctamente.'
            });
        }

        log.exito('Descarga finalizada correctamente. Iniciando análisis y procesamiento del video...');

        // Obtenemos la duración total del video descargado
        const duracionTotal = await obtenerDuracionVideo(rutaVideoDescargado);
        log.info(`Duración total del video: ${formatoDuracion(duracionTotal)}`);

        // Definimos la duración de cada parte y calculamos cuántas se van a generar
        const duracionParte = config.CLIP_DURATION || 60;
        const cantidadPartes = Math.ceil(duracionTotal / duracionParte);
        log.info(`Se dividirá el video en ${cantidadPartes} partes de ${duracionParte} segundos cada una`);

        // Array para guardar la información de las partes generadas
        const listaPartesGeneradas = [];

        // Generamos cada parte una por una
        for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
            log.info(`\n🔹 PROCESANDO PARTE ${numeroParte}/${cantidadPartes}`);

            try {
                // Llamamos a la función que se encarga de cortar y procesar el segmento
                const rutaParte = await extraerSegmento(rutaVideoDescargado, numeroParte, titulo);
                
                if (rutaParte && archivoEsValido(rutaParte)) {
                    listaPartesGeneradas.push({
                        numero: numeroParte,
                        ruta: rutaParte
                    });
                    log.exito(`Parte ${numeroParte} generada correctamente`);
                } else {
                    log.error(`La parte ${numeroParte} se generó pero es inválida o no se guardó correctamente`);
                }

            } catch (error) {
                log.error(`No se pudo generar la parte ${numeroParte}`, error);
                continue;
            }
        }

        // Verificamos si se generó al menos una parte correctamente
        if (listaPartesGeneradas.length === 0) {
            log.error('No se pudo generar ninguna parte del video');
            return res.json({
                status: 'error',
                mensaje: '❌ Ocurrieron errores al dividir el video, no se pudo generar ningún archivo válido'
            });
        }

        log.exito(`\n✅ Proceso de corte finalizado. Se generaron ${listaPartesGeneradas.length} partes de un total de ${cantidadPartes} planificadas`);

        // Iniciamos el envío de los archivos a los canales de Telegram
        log.info('📤 Iniciando envío de archivos a los canales configurados...');

        for (const parte of listaPartesGeneradas) {
            // Armamos el mensaje que se enviará junto con el archivo
            const mensajeTelegram = `🎬 <b>${titulo}</b>\n📌 Parte ${parte.numero} de ${listaPartesGeneradas.length}\n⏱️ Duración: ${duracionParte} segundos\n🔹 Procesado automáticamente por MallyCuts`;

            try {
                // Enviamos el archivo a los dos canales
                await enviarADosCanales(parte.ruta, mensajeTelegram, parte.numero);
                log.exito(`Parte ${parte.numero} enviada correctamente a los canales`);
            } catch (error) {
                log.error(`No se pudo enviar la parte ${parte.numero}`, error);
            }

            // Eliminamos el archivo temporal para liberar espacio en el disco
            if (archivoEsValido(parte.ruta)) {
                fs.unlinkSync(parte.ruta);
                log.detalle(`Archivo temporal de la parte ${parte.numero} eliminado`);
            }

            // Esperamos unos segundos entre envíos para no saturar la API de Telegram
            await new Promise(resolve => setTimeout(resolve, 3000));
        }

        // Eliminamos el archivo original descargado para liberar espacio
        if (config.BORRAR_ARCHIVO_ORIGINAL !== false && archivoEsValido(rutaVideoDescargado)) {
            fs.unlinkSync(rutaVideoDescargado);
            log.detalle('Archivo original descargado eliminado del sistema');
        }

        log.separador('✅ PROCESO COMPLETADO CON ÉXITO');

        // Respondemos a la solicitud indicando que todo finalizó bien
        return res.json({
            status: 'ok',
            mensaje: `✅ El video fue procesado correctamente. Se enviaron ${listaPartesGeneradas.length} partes a tus canales de Telegram.`
        });

    } catch (errorGeneral) {
        log.error('Error general al procesar el enlace', errorGeneral);
        return res.json({
            status: 'error',
            mensaje: `❌ Ocurrió un error inesperado: ${errorGeneral.message}`
        });
    }
});

module.exports = router;
