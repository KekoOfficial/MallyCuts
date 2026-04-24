// 📤 RUTAS Y FUNCIONES PARA PROCESAR ARCHIVOS SUBIDOS
// Recibe archivos de video, los procesa, divide y envía a los canales configurados

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const router = express.Router();

// Importamos módulos del sistema
const log = require('../js/logger');
const config = require('../config');
const {
    obtenerDuracionVideo,
    formatoDuracion,
    archivoEsValido,
    obtenerTamanoArchivoMB
} = require('./utilidades');
const { extraerSegmento } = require('../core/cortar');
const { enviarADosCanales } = require('../core/enviar');

// ==============================================
// CONFIGURACIÓN DE LA SUBIDA DE ARCHIVOS
// ==============================================

// Definimos dónde se guardarán y cómo se nombrarán los archivos
const almacenamiento = multer.diskStorage({
    // Carpeta de destino para los archivos subidos
    destination: (req, archivo, callback) => {
        log.detalle('Preparando espacio para guardar el archivo...');
        callback(null, config.INPUT_FOLDER);
    },

    // Reglas para generar el nombre del archivo
    filename: (req, archivo, callback) => {
        let tituloArchivo = req.body.titulo?.trim() || 'video_sin_titulo';

        // Eliminamos caracteres que no se pueden usar en nombres de archivos
        tituloArchivo = tituloArchivo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        tituloArchivo = tituloArchivo.substring(0, 100); // Limitamos longitud máxima

        // Agregamos marca de tiempo para evitar duplicados
        const nombreFinal = `${tituloArchivo}_${Date.now()}.mp4`;
        log.detalle(`Nombre asignado al archivo: ${nombreFinal}`);

        callback(null, nombreFinal);
    }
});

// Filtramos qué tipos de archivos se aceptan
const filtroArchivos = (req, archivo, callback) => {
    const formatosPermitidos = [
        'video/mp4', 'video/mkv', 'video/avi', 'video/mov',
        'video/flv', 'video/wmv', 'video/mpeg', 'video/webm'
    ];

    if (formatosPermitidos.includes(archivo.mimetype)) {
        log.exito(`Formato de archivo válido: ${archivo.mimetype}`);
        callback(null, true);
    } else {
        log.error(`Formato no permitido: ${archivo.mimetype}. Solo se aceptan archivos de video.`);
        callback(new Error('Formato de archivo no permitido'), false);
    }
};

// ⚠️ NOMBRE DEL CAMPO QUE DEBE COINCIDIR EXACTAMENTE CON EL FRONTEND
const NOMBRE_CAMPO_ARCHIVO = 'archivo_video';

// Configuración final de multer
const subirArchivo = multer({
    storage: almacenamiento,
    fileFilter: filtroArchivos,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024, // Límite máximo: 10 GB
        parts: 100,
        headerPairs: 2000
    }
}).single(NOMBRE_CAMPO_ARCHIVO);

// ==============================================
// RUTA PRINCIPAL DE PROCESAMIENTO
// ==============================================

/**
 * Recibe el archivo subido, lo analiza, lo divide en partes y lo envía a los canales
 */
router.post('/procesar', (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ARCHIVO');
    log.aviso('Los videos largos pueden tardar varios minutos o incluso horas en procesarse. Tené paciencia.');

    // Ejecutamos la subida del archivo
    subirArchivo(req, res, async (errorSubida) => {
        try {
            // Manejamos errores durante la subida
            if (errorSubida) {
                log.error('Error al subir el archivo', errorSubida);
                let mensajeError = `❌ No se pudo subir el archivo: ${errorSubida.message}`;

                // Mensaje específico para el error de nombre de campo incorrecto
                if (errorSubida.message === 'Unexpected field' || errorSubida.code === 'LIMIT_UNEXPECTED_FILE') {
                    mensajeError = `❌ ERROR DE CONFIGURACIÓN: El nombre del campo del archivo no coincide. 
                    El servidor espera que se envíe con el nombre: "${NOMBRE_CAMPO_ARCHIVO}"`;
                }
                // Mensaje específico cuando el archivo supera el límite de tamaño
                else if (errorSubida.code === 'LIMIT_FILE_SIZE') {
                    mensajeError = `❌ El archivo supera el límite máximo de 10 GB. Podés modificar este valor en el archivo de configuración.`;
                }

                return res.json({
                    status: 'error',
                    mensaje: mensajeError
                });
            }

            // Verificamos que se hayan enviado todos los datos obligatorios
            if (!req.body?.titulo || !req.file) {
                log.error('Faltan datos: no se recibió el título o el archivo de video');
                return res.json({
                    status: 'error',
                    mensaje: '❌ Debés ingresar un título y seleccionar un archivo de video para procesar.'
                });
            }

            // Mostramos información del archivo recibido
            const tamanoArchivo = obtenerTamanoArchivoMB(req.file.path);
            log.info('Datos recibidos correctamente:');
            log.detalle(`Título del video: ${req.body.titulo.trim()}`);
            log.detalle(`Nombre del archivo: ${req.file.filename}`);
            log.detalle(`Tamaño del archivo: ${tamanoArchivo}`);

            // Guardamos valores para usarlos en todo el proceso
            const tituloVideo = req.body.titulo.trim();
            const rutaArchivoOriginal = path.join(config.INPUT_FOLDER, req.file.filename);

            // Verificamos que el archivo se haya guardado correctamente y no esté dañado
            if (!archivoEsValido(rutaArchivoOriginal)) {
                log.error('El archivo subido está dañado o no se guardó correctamente');
                return res.json({
                    status: 'error',
                    mensaje: '❌ El archivo no es válido o se guardó incorrectamente. Intentá nuevamente.'
                });
            }

            // Obtenemos la duración total del video
            log.info('Analizando archivo para obtener información...');
            let duracionTotal;
            try {
                duracionTotal = await obtenerDuracionVideo(rutaArchivoOriginal);
                log.exito(`Duración total del video: ${formatoDuracion(duracionTotal)}`);
            } catch (error) {
                log.error('No se pudo leer la duración del video', error);
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo leer la información del video. Probablemente esté dañado o no sea un archivo de video válido.'
                });
            }

            // Calculamos cuántas partes se van a generar
            const duracionParte = config.CLIP_DURATION || 60;
            const cantidadPartes = Math.ceil(duracionTotal / duracionParte);
            log.info(`Se dividirá el video en ${cantidadPartes} partes de ${duracionParte} segundos cada una`);

            // Array para guardar las rutas de las partes generadas
            const listaPartesGeneradas = [];

            // Iniciamos el proceso de corte y procesamiento
            log.info('\n🔹 INICIANDO CORTE Y PROCESAMIENTO DE PARTES');
            for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
                log.info(`\nProcesando parte ${numeroParte} de ${cantidadPartes}`);

                try {
                    // Extraemos el segmento correspondiente
                    const rutaParte = await extraerSegmento(
                        rutaArchivoOriginal,
                        numeroParte,
                        tituloVideo,
                        duracionParte,
                        config.VELOCIDAD_PREDETERMINADA
                    );

                    // Verificamos que la parte generada sea válida
                    if (rutaParte && archivoEsValido(rutaParte)) {
                        listaPartesGeneradas.push({
                            numero: numeroParte,
                            ruta: rutaParte
                        });
                        log.exito(`Parte ${numeroParte} generada correctamente | Tamaño: ${obtenerTamanoArchivoMB(rutaParte)}`);
                    } else {
                        log.error(`La parte ${numeroParte} no se generó correctamente o quedó vacía`);
                    }

                } catch (error) {
                    log.error(`Error al generar la parte ${numeroParte}`, error);
                    continue;
                }
            }

            // Verificamos si se generó al menos una parte válida
            if (listaPartesGeneradas.length === 0) {
                log.error('No se pudo generar ninguna parte válida del video');
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo dividir el video. Ocurrieron errores en todas las partes.'
                });
            }

            log.exito(`\n✅ Proceso de corte finalizado. Se generaron ${listaPartesGeneradas.length} partes válidas de un total de ${cantidadPartes} planificadas`);

            // Iniciamos el envío de las partes a los canales de Telegram
            log.info('\n📤 INICIANDO ENVÍO A LOS CANALES DE TELEGRAM');

            for (const parte of listaPartesGeneradas) {
                // Creamos el mensaje que acompañará a cada archivo
                const mensajeTelegram = `🎬 <b>${tituloVideo}</b>
📌 Parte ${parte.numero} de ${listaPartesGeneradas.length}
⏱️ Duración: ${duracionParte} segundos
⚡ Velocidad: ${config.VELOCIDAD_PREDETERMINADA}x
🔹 ${config.TEXTO_MARCA_PREDETERMINADA}`;

                try {
                    // Enviamos el archivo a los dos canales configurados
                    await enviarADosCanales(parte.ruta, mensajeTelegram, parte.numero);
                    log.exito(`Parte ${parte.numero} enviada correctamente a los canales`);
                } catch (error) {
                    log.error(`No se pudo enviar la parte ${parte.numero}`, error);
                }

                // Eliminamos el archivo temporal para liberar espacio
                if (archivoEsValido(parte.ruta)) {
                    fs.unlinkSync(parte.ruta);
                    log.detalle(`Archivo temporal de la parte ${parte.numero} eliminado`);
                }

                // Esperamos 3 segundos entre envíos para no saturar la API de Telegram
                await new Promise(resolve => setTimeout(resolve, 3000));
            }

            // Eliminamos el archivo original si está configurado así
            if (config.BORRAR_ARCHIVOS_DESPUES && archivoEsValido(rutaArchivoOriginal)) {
                fs.unlinkSync(rutaArchivoOriginal);
                log.detalle('Archivo original subido eliminado del sistema');
            }

            log.separador('✅ PROCESO COMPLETADO CON ÉXITO');

            // Respondemos al usuario que todo terminó correctamente
            return res.json({
                status: 'ok',
                mensaje: `✅ Proceso finalizado. Se enviaron ${listaPartesGeneradas.length} partes a tus canales de Telegram.`
            });

        } catch (errorGeneral) {
            log.error('Error general en el proceso', errorGeneral);
            return res.json({
                status: 'error',
                mensaje: `❌ Ocurrió un error inesperado: ${errorGeneral.message}`
            });
        }
    });
});

module.exports = router;
