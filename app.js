// 🚀 SERVIDOR PRINCIPAL - MallyCuts
// Sistema para procesar videos largos, dividirlos y enviarlos automáticamente

// Importamos las dependencias necesarias
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');

// 🔹 Sistema de logs personalizado
const log = require('./js/logger');

// 🔹 Cargamos la configuración del proyecto
let config;
try {
    config = require('./config');
    log.exito('Archivo de configuración cargado correctamente');
    log.detalle(`Carpeta de archivos originales: ${config.ORIGINAL_FOLDER || config.ORIGINAL_FOLDER || 'No definida'}`);
    log.detalle(`Carpeta de archivos procesados: ${config.TEMP_FOLDER || config.TEMP_FOLDER || 'No definida'}`);
} catch (error) {
    log.error('No se pudo cargar el archivo de configuración', error);
    process.exit(1);
}

// 🔹 Cargamos los módulos de procesamiento
let procesarEnlace, extraerSegmento, enviarArchivo, enviarADosCanales;
try {
    const descargarModulo = require('./core/descargar');
    const cortarModulo = require('./core/cortar');
    const enviarModulo = require('./core/enviar');
    
    procesarEnlace = descargarModulo.procesarEnlace;
    extraerSegmento = cortarModulo.extraerSegmento;
    enviarArchivo = enviarModulo.enviarArchivo;
    enviarADosCanales = enviarModulo.enviarADosCanales;
    
    log.exito('Todos los módulos del sistema cargados correctamente');
} catch (error) {
    log.error('No se pudieron cargar los archivos de la carpeta core', error);
    process.exit(1);
}

// Inicializamos la aplicación Express
const app = express();
const PUERTO = 3000;

// ==============================================
// CONFIGURACIÓN GENERAL
// ==============================================

// 🔹 Ocultamos mensajes internos innecesarios de Express
process.env.DEBUG = '';

// 🚀 Límites ampliados para soportar archivos grandes
app.use(express.json({ limit: '10000mb' }));
app.use(express.urlencoded({ extended: true, limit: '10000mb' }));

// 📁 Servimos los archivos estáticos de la página web
app.use(express.static(path.join(__dirname, 'public')));

// ⏱️ Tiempos de espera ampliados para procesos largos
app.use((req, res, next) => {
    req.setTimeout(3600000); // 1 hora de espera
    res.setTimeout(3600000);
    res.timeout = 3600000;
    next();
});

// ⚠️ Manejo global de errores
app.use((err, req, res, next) => {
    log.error('Error general en el servidor', err);
    res.status(500).json({
        status: 'error',
        mensaje: '❌ Ocurrió un error inesperado en el servidor'
    });
});

// 📂 Creamos todas las carpetas necesarias si no existen
const carpetasNecesarias = [
    config.ORIGINAL_FOLDER || config.ORIGINAL_FOLDER,
    config.TEMP_FOLDER || config.TEMP_FOLDER,
    config.INPUT_FOLDER,
    config.TEMP_UPLOAD_FOLDER
];

carpetasNecesarias.forEach(rutaCarpeta => {
    if (!rutaCarpeta) return;
    try {
        if (!fs.existsSync(rutaCarpeta)) {
            fs.mkdirSync(rutaCarpeta, { recursive: true, mode: 0o777 });
            log.exito(`Carpeta creada: ${rutaCarpeta}`);
        } else {
            log.detalle(`Carpeta ya disponible: ${rutaCarpeta}`);
        }
    } catch (error) {
        log.error(`No se pudo crear o acceder a la carpeta: ${rutaCarpeta}`, error);
    }
});

// ==============================================
// CONFIGURACIÓN DE SUBIDA DE ARCHIVOS
// ==============================================
const almacenamiento = multer.diskStorage({
    destination: (req, archivo, callback) => {
        log.detalle('Preparando espacio para guardar el archivo...');
        callback(null, config.INPUT_FOLDER);
    },
    filename: (req, archivo, callback) => {
        let titulo = req.body.titulo?.trim() || 'video_sin_titulo';
        // Limpiamos caracteres que no se pueden usar en nombres de archivos
        titulo = titulo.replace(/[<>:"/\\|?*\n\r]/g, ' ').substring(0, 100);
        const nombreFinal = `${titulo}_${Date.now()}.mp4`;
        log.detalle(`Nombre asignado al archivo: ${nombreFinal}`);
        callback(null, nombreFinal);
    }
});

const filtroArchivos = (req, archivo, callback) => {
    const formatosPermitidos = ['video/mp4', 'video/mkv', 'video/avi', 'video/mov', 'video/flv', 'video/wmv'];
    if (formatosPermitidos.includes(archivo.mimetype)) {
        log.exito(`Formato de archivo válido: ${archivo.mimetype}`);
        callback(null, true);
    } else {
        log.error(`Formato no permitido: ${archivo.mimetype}. Solo se aceptan archivos de video.`);
        callback(new Error('Formato de archivo no permitido'), false);
    }
};

// 🚀 Límite de tamaño: 10 GB
const subirArchivo = multer({
    storage: almacenamiento,
    fileFilter: filtroArchivos,
    limits: {
        fileSize: 10 * 1024 * 1024 * 1024,
        parts: 100,
        headerPairs: 2000
    }
}).single('archivo_video');

// ==============================================
// RUTA: PROCESAR ARCHIVOS SUBIDOS
// ==============================================
app.post('/procesar', (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ARCHIVO');
    log.aviso('Los videos largos pueden tardar varios minutos o incluso horas en procesarse. Ten paciencia.');

    subirArchivo(req, res, async (errorSubida) => {
        try {
            // Manejamos errores de subida
            if (errorSubida) {
                log.error('Error al subir el archivo', errorSubida);
                let mensaje = `❌ No se pudo subir el archivo: ${errorSubida.message}`;

                if (errorSubida.code === 'LIMIT_FILE_SIZE') {
                    mensaje = `❌ El archivo es demasiado grande. El límite actual es de 10 GB. Si necesitas más capacidad, avísame.`;
                }

                return res.json({
                    status: 'error',
                    mensaje: mensaje
                });
            }

            // Verificamos que tengamos todos los datos
            if (!req.body?.titulo || !req.file) {
                log.error('Faltan datos: no se envió el título o el archivo');
                return res.json({
                    status: 'error',
                    mensaje: '❌ Debes ingresar un título y seleccionar un archivo de video'
                });
            }

            // Mostramos información del archivo recibido
            const tamañoGB = (req.file.size / (1024 * 1024 * 1024)).toFixed(2);
            log.info('Datos recibidos correctamente:');
            log.detalle(`Título: ${req.body.titulo}`);
            log.detalle(`Archivo: ${req.file.filename}`);
            log.detalle(`Tamaño: ${tamañoGB} GB`);

            const tituloVideo = req.body.titulo.trim();
            const rutaArchivoOriginal = path.join(config.INPUT_FOLDER, req.file.filename);

            // Verificamos que el archivo se haya guardado bien
            if (!fs.existsSync(rutaArchivoOriginal)) {
                log.error('El archivo no se guardó correctamente en el sistema');
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo guardar el archivo en el servidor'
                });
            }

            // Obtenemos la duración total del video
            log.info('Analizando información del video...');
            let duracionTotal;
            try {
                duracionTotal = await obtenerDuracionVideo(rutaArchivoOriginal);
                const horas = Math.floor(duracionTotal / 3600);
                const minutos = Math.floor((duracionTotal % 3600) / 60);
                const segundos = Math.floor(duracionTotal % 60);
                log.exito(`Duración total: ${horas}h ${minutos}m ${segundos}s`);
            } catch (error) {
                log.error('No se pudo leer la duración del video', error);
                return res.json({
                    status: 'error',
                    mensaje: '❌ El archivo de video está dañado o no es válido'
                });
            }

            // Calculamos cuántas partes se van a generar
            const duracionParte = config.CLIP_DURATION || 60;
            const cantidadPartes = Math.ceil(duracionTotal / duracionParte);
            log.info(`Se dividirá en ${cantidadPartes} partes de ${duracionParte} segundos cada una`);

            const listaPartesGeneradas = [];

            // Procesamos cada parte una por una
            for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
                log.info(`\n🔹 PROCESANDO PARTE ${numeroParte}/${cantidadPartes}`);

                try {
                    const rutaParte = await extraerSegmento(rutaArchivoOriginal, numeroParte, tituloVideo);
                    if (rutaParte) {
                        listaPartesGeneradas.push({
                            numero: numeroParte,
                            ruta: rutaParte
                        });
                    }
                } catch (error) {
                    log.error(`No se pudo generar la parte ${numeroParte}`, error);
                    continue;
                }
            }

            // Verificamos cuántas partes se generaron correctamente
            if (listaPartesGeneradas.length === 0) {
                log.error('No se generó ninguna parte del video');
                return res.json({
                    status: 'error',
                    mensaje: '❌ Ocurrieron errores al dividir el video'
                });
            }

            log.exito(`\n✅ Proceso de corte finalizado. Se generaron ${listaPartesGeneradas.length} partes correctamente`);

            // Enviamos las partes a los canales de Telegram
            log.info('📤 Iniciando envío de archivos a Telegram...');

            for (const parte of listaPartesGeneradas) {
                const mensajeTelegram = `🎬 <b>${tituloVideo}</b>\n📌 Parte ${parte.numero} de ${listaPartesGeneradas.length}\n⏱️ Duración: ${duracionParte} segundos\n🔹 Procesado automáticamente por MallyCuts`;

                try {
                    await enviarADosCanales(parte.ruta, mensajeTelegram, parte.numero);
                    log.exito(`Parte ${parte.numero} enviada correctamente`);
                } catch (error) {
                    log.error(`No se pudo enviar la parte ${parte.numero}`, error);
                }

                // Eliminamos el archivo temporal para liberar espacio
                if (fs.existsSync(parte.ruta)) {
                    fs.unlinkSync(parte.ruta);
                    log.detalle(`Archivo temporal de la parte ${parte.numero} eliminado`);
                }

                // Esperamos unos segundos entre envíos para no saturar la API
                await new Promise(resolve => setTimeout(resolve, 3000));
            }

            // Eliminamos el archivo original para liberar espacio
            if (config.BORRAR_ARCHIVO_ORIGINAL !== false && fs.existsSync(rutaArchivoOriginal)) {
                fs.unlinkSync(rutaArchivoOriginal);
                log.detalle('Archivo original eliminado del sistema');
            }

            log.separador('✅ PROCESO COMPLETADO CON ÉXITO');

            return res.json({
                status: 'ok',
                mensaje: `✅ El video fue procesado correctamente. Se enviaron ${listaPartesGeneradas.length} partes a tus canales.`
            });

        } catch (errorGeneral) {
            log.error('Error general al procesar el archivo', errorGeneral);
            return res.json({
                status: 'error',
                mensaje: `❌ Ocurrió un error: ${errorGeneral.message}`
            });
        }
    });
});

// ==============================================
// RUTA: PROCESAR ENLACES DE DESCARGA
// ==============================================
app.post('/procesar-enlace', async (req, res) => {
    log.separador('📥 NUEVA SOLICITUD: PROCESAR ENLACE');

    try {
        if (!req.body?.enlace || !req.body?.titulo) {
            log.error('Faltan datos: no se envió el enlace o el título');
            return res.json({
                status: 'error',
                mensaje: '❌ Debes ingresar el enlace y el título del video'
            });
        }

        const { enlace, titulo } = req.body;
        log.info(`Enlace recibido: ${enlace}`);
        log.info(`Título: ${titulo}`);

        log.aviso('Iniciando descarga... Esto puede tardar bastante dependiendo del tamaño del video y la velocidad de internet');

        // Llamamos al módulo de descarga
        const rutaVideoDescargado = await procesarEnlace(enlace, titulo);

        if (!rutaVideoDescargado || !fs.existsSync(rutaVideoDescargado)) {
            log.error('No se pudo descargar el video');
            return res.json({
                status: 'error',
                mensaje: '❌ Falló la descarga del video'
            });
        }

        log.exito('Descarga finalizada. Iniciando procesamiento...');

        // A partir de acá hacemos lo mismo que con los archivos subidos
        const duracionTotal = await obtenerDuracionVideo(rutaVideoDescargado);
        const duracionParte = config.CLIP_DURATION || 60;
        const cantidadPartes = Math.ceil(duracionTotal / duracionParte);

        const listaPartes = [];
        for (let i = 1; i <= cantidadPartes; i++) {
            try {
                const rutaParte = await extraerSegmento(rutaVideoDescargado, i, titulo);
                if (rutaParte) listaPartes.push({ numero: i, ruta: rutaParte });
            } catch (error) {
                log.error(`Error al generar parte ${i}`, error);
            }
        }

        // Enviamos las partes
        for (const parte of listaPartes) {
            const mensaje = `🎬 <b>${titulo}</b>\n📌 Parte ${parte.numero} de ${listaPartes.length}\n🔹 Procesado automáticamente por MallyCuts`;
            try {
                await enviarADosCanales(parte.ruta, mensaje, parte.numero);
                log.exito(`Parte ${parte.numero} enviada`);
            } catch (error) {
                log.error(`Error al enviar parte ${parte.numero}`, error);
            }
            if (fs.existsSync(parte.ruta)) fs.unlinkSync(parte.ruta);
            await new Promise(resolve => setTimeout(resolve, 3000));
        }

        if (config.BORRAR_ARCHIVO_ORIGINAL !== false && fs.existsSync(rutaVideoDescargado)) {
            fs.unlinkSync(rutaVideoDescargado);
        }

        log.separador('✅ ENLACE PROCESADO CON ÉXITO');

        return res.json({
            status: 'ok',
            mensaje: `✅ El video del enlace fue procesado y enviado correctamente`
        });

    } catch (error) {
        log.error('Error al procesar el enlace', error);
