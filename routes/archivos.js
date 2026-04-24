// 📤 RUTAS Y FUNCIONES PARA PROCESAR ARCHIVOS SUBIDOS
// Se encarga de recibir el archivo, analizarlo, dividirlo y enviarlo a los canales

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const router = express.Router();

// Importamos dependencias y módulos del sistema
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
// CONFIGURACIÓN DE SUBIDA DE ARCHIVOS
// ==============================================

// Definimos dónde y cómo se guardarán los archivos
const almacenamiento = multer.diskStorage({
    // Carpeta donde se guardarán temporalmente los archivos subidos
    destination: (req, archivo, callback) => {
        log.detalle('Preparando espacio para guardar el archivo...');
        callback(null, config.INPUT_FOLDER);
    },

    // Definimos el nombre que tendrá el archivo guardado
    filename: (req, archivo, callback) => {
        let tituloArchivo = req.body.titulo?.trim() || 'video_sin_titulo';
        
        // Eliminamos caracteres que no se pueden usar en nombres de archivos
        tituloArchivo = tituloArchivo.replace(/[<>:"/\\|?*\n\r\t]/g, ' ').trim();
        tituloArchivo = tituloArchivo.substring(0, 100); // Limitamos la longitud
        
        // Agregamos marca de tiempo para evitar nombres repetidos
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

// Configuración final de multer con límite de tamaño
const subirArchivo = multer({
    storage: almacenamiento,
    fileFilter: filtroArchivos,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024, // 10 GB máximo
        parts: 100,
        headerPairs: 2000
    }
}).single('archivo_video'); // El nombre del campo que se enviará desde el formulario

// ==============================================
// RUTA PRINCIPAL DE PROCESAMIENTO
// ==============================================

/**
 * Recibe el archivo subido, lo procesa y lo envía
 */
router.post('/procesar', (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ARCHIVO');
    log.aviso('Los videos largos pueden tardar varios minutos o incluso horas en procesarse. Tené paciencia.');

    // Ejecutamos el proceso de subida
    subirArchivo(req, res, async (errorSubida) => {
        try {
            // Manejamos errores durante la subida
            if (errorSubida) {
                log.error('Error al subir el archivo', errorSubida);
                let mensajeError = `❌ No se pudo subir el archivo: ${errorSubida.message}`;

                // Mensaje específico si el archivo supera el tamaño límite
                if (errorSubida.code === 'LIMIT_FILE_SIZE') {
                    mensajeError = `❌ El archivo supera el límite máximo de 10 GB. Si necesitás más capacidad, podés modificar la configuración.`;
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
            log.detalle(`Tamaño: ${tamanoArchivo}`);

            // Guardamos los datos para usarlos más adelante
            const tituloVideo = req.body.titulo.trim();
            const rutaArchivoOriginal = path.join(config.INPUT_FOLDER, req.file.filename);

            // Verificamos que el archivo se haya guardado correctamente
            if (!archivoEsValido(rutaArchivoOriginal)) {
                log.error('El archivo subido no se guardó correctamente o está dañado');
                return res.json({
                    status: 'error',
                    mensaje: '❌ El archivo no se guardó correctamente o es inválido. Intentá nuevamente.'
                });
            }

            // Obtenemos la duración total del video
            log.info('Analizando el archivo para obtener sus datos...');
            let duracionTotal;
            try {
                duracionTotal = await obtenerDuracionVideo(rutaArchivoOriginal);
                log.exito(`Duración total del video: ${formatoDuracion(duracionTotal)}`);
            } catch (error) {
                log.error('No se pudo leer la duración del video', error);
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo leer la información del video. Probablemente el archivo esté dañado o no sea un archivo de video válido.'
                });
            }

            // Calculamos la cantidad de partes que se generarán
            const duracionParte = config.CLIP_DURATION || 60; // 60 segundos por defecto
            const cantidadPartes = Math.ceil(duracionTotal / duracionParte);
            log.info(`Se dividirá el video en ${cantidadPartes} partes de ${duracionParte} segundos cada una`);

            // Array para guardar los datos de las partes generadas
            const listaPartesGeneradas = [];

            // Generamos cada parte una por una
            log.info('\n🔹 INICIANDO PROCESO DE CORTE Y PROCESAMIENTO');
            for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
                log.info(`\nProcesando parte ${numeroParte} de ${cantidadPartes}`);

                try {
                    // Llamamos a la función que crea el segmento
                    const rutaParte = await extraerSegmento(rutaArchivoOriginal, numeroParte, tituloVideo);

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
            log.info('\n📤 INICIANDO ENVÍO DE ARCHIVOS A TELEGRAM');

            for (const parte of listaPartesGeneradas) {
                // Creamos el mensaje que acompañará al archivo
                const mensajeTelegram = `🎬 <b>${tituloVideo}</b>
📌 Parte ${parte.numero} de ${listaPartesGeneradas.length}
⏱️ Duración: ${duracionParte} segundos
🔹 Procesado automáticamente por MallyCuts`;

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

            // Eliminamos el archivo original subido para liberar espacio
            if (config.BORRAR_ARCHIVO_ORIGINAL !== false && archivoEsValido(rutaArchivoOriginal)) {
                fs.unlinkSync(rutaArchivoOriginal);
                log.detalle('Archivo original subido eliminado del sistema');
            }

            log.separador('✅ PROCESO COMPLETADO CON ÉXITO');

            // Respondemos al usuario que todo finalizó bien
            return res.json({
                status: 'ok',
                mensaje: `✅ El video fue procesado correctamente. Se enviaron ${listaPartesGeneradas.length} partes a tus canales de Telegram.`
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
