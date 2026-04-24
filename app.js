// Importamos las dependencias necesarias
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { execFile } = require('child_process');

// Cargamos configuración
let config;
try {
    config = require('./config');
    console.log("✅ Archivo de configuración cargado");
    console.log("📂 Carpeta originales:", config.ORIGINAL_FOLDER);
    console.log("📂 Carpeta procesados/temporales:", config.TEMP_FOLDER);
} catch (error) {
    console.error("❌ ERROR: No se pudo cargar config.js:", error.message);
    process.exit(1);
}

// Cargamos módulos de la carpeta core
let procesarEnlace, extraerSegmento, enviarADosCanales;
try {
    const descargar = require('./core/descargar');
    const cortar = require('./core/cortar');
    const enviar = require('./core/enviar');
    
    procesarEnlace = descargar.procesarEnlace;
    extraerSegmento = cortar.extraerSegmento;
    enviarADosCanales = enviar.enviarADosCanales;
    
    console.log("✅ Módulos de la carpeta core cargados correctamente");
} catch (error) {
    console.error("❌ ERROR al cargar módulos core:", error.message);
    process.exit(1);
}

// Inicializamos la aplicación
const app = express();
const PUERTO = 3000;

// ==============================================
// CONFIGURACIÓN GENERAL
// ==============================================
app.use(express.json({ limit: '500mb' }));
app.use(express.urlencoded({ extended: true, limit: '500mb' }));
app.use(express.static(path.join(__dirname, 'public')));

// Capturamos errores generales
app.use((err, req, res, next) => {
    console.error("❌ ERROR GENERAL:", err.message);
    res.json({ status: 'error', mensaje: '❌ Ocurrió un error en el servidor' });
});

// Creamos las carpetas si no existen (usando los nombres de tu configuración)
const carpetas = [
    config.ORIGINAL_FOLDER,
    config.TEMP_FOLDER,
    config.INPUT_FOLDER,
    config.TEMP_UPLOAD_FOLDER
];

carpetas.forEach(carpeta => {
    try {
        if (!fs.existsSync(carpeta)) {
            fs.mkdirSync(carpeta, { recursive: true, mode: 0o777 });
            console.log(`📁 Carpeta creada: ${carpeta}`);
        } else {
            console.log(`📁 Carpeta ya existe: ${carpeta}`);
        }
    } catch (error) {
        console.error(`❌ No se pudo crear la carpeta ${carpeta}:`, error.message);
    }
});

// ==============================================
// CONFIGURACIÓN DE SUBIDA DE ARCHIVOS
// ==============================================
const almacenamientoArchivos = multer.diskStorage({
    destination: (req, file, cb) => {
        console.log("📂 Guardando archivo en carpeta de entrada");
        cb(null, config.INPUT_FOLDER);
    },
    filename: (req, file, cb) => {
        let tituloArchivo = req.body.titulo?.trim() || 'video_sin_titulo';
        tituloArchivo = tituloArchivo.replace(/[<>:"/\\|?*\n\r]/g, ' ').substring(0, 100);
        const nombreFinal = `${tituloArchivo}_${Date.now()}.mp4`;
        console.log("📄 Nombre del archivo a guardar:", nombreFinal);
        cb(null, nombreFinal);
    }
});

const filtroArchivos = (req, file, cb) => {
    const tiposPermitidos = ['video/mp4', 'video/mkv', 'video/avi', 'video/mov'];
    if (tiposPermitidos.includes(file.mimetype)) {
        console.log("✅ Tipo de archivo válido:", file.mimetype);
        cb(null, true);
    } else {
        console.log("❌ Tipo de archivo no permitido:", file.mimetype);
        cb(new Error('Solo se aceptan archivos de video'), false);
    }
};

const subirArchivo = multer({
    storage: almacenamientoArchivos,
    fileFilter: filtroArchivos,
    limits: { fileSize: 500 * 1024 * 1024 }
}).single('video');

// ==============================================
// RUTA PARA PROCESAR ARCHIVOS SUBIDOS
// ==============================================
app.post('/procesar', (req, res) => {
    console.log("\n📥 RECIBIDA SOLICITUD DE PROCESAR ARCHIVO");
    
    subirArchivo(req, res, async (err) => {
        try {
            // Error al subir el archivo
            if (err) {
                console.error("❌ ERROR AL SUBIR EL ARCHIVO:", err.message);
                return res.json({
                    status: 'error',
                    mensaje: `❌ Error al subir: ${err.message}`
                });
            }

            // Verificamos que tengamos los datos
            console.log("📋 Datos recibidos:");
            console.log("Título:", req.body?.titulo);
            console.log("Archivo:", req.file?.filename);

            if (!req.body?.titulo || !req.file) {
                console.error("❌ Faltan datos: título o archivo no enviados");
                return res.json({
                    status: 'error',
                    mensaje: '❌ Debes completar el título y seleccionar el archivo'
                });
            }

            const tituloOriginal = req.body.titulo.trim();
            const rutaArchivoOriginal = path.join(config.INPUT_FOLDER, req.file.filename);
            console.log("📂 Ruta completa del archivo:", rutaArchivoOriginal);

            // Verificamos que el archivo se guardó
            if (!fs.existsSync(rutaArchivoOriginal)) {
                console.error("❌ El archivo no se guardó correctamente en la ruta indicada");
                return res.json({
                    status: 'error',
                    mensaje: '❌ No se pudo guardar el archivo'
                });
            }

            // Obtenemos duración del video
            console.log("⏱️ Obteniendo duración del video...");
            let duracionTotal;
            try {
                duracionTotal = await obtenerDuracionVideo(rutaArchivoOriginal);
                console.log(`✅ Duración obtenida: ${Math.round(duracionTotal)} segundos`);
            } catch (error) {
                console.error("❌ No se pudo leer la duración:", error.message);
                return res.json({
                    status: 'error',
                    mensaje: '❌ El archivo de video está dañado o no es válido'
                });
            }

            const duracionSegmento = config.CLIP_DURATION || 60;
            const cantidadPartes = Math.floor(duracionTotal / duracionSegmento) + 1;
            console.log(`✂️ Se generarán ${cantidadPartes} partes de ${duracionSegmento} segundos cada una`);

            // Procesamos cada parte
            const listaPartes = [];
            for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
                console.log(`🔄 Procesando parte ${numeroParte}/${cantidadPartes}`);
                
                let rutaParte;
                try {
                    rutaParte = await extraerSegmento(rutaArchivoOriginal, numeroParte, tituloOriginal);
                    console.log(`✅ Parte ${numeroParte} generada: ${rutaParte}`);
                } catch (error) {
                    console.error(`❌ Error al generar la parte ${numeroParte}:`, error.message);
                    continue;
                }
                
                if (rutaParte && fs.existsSync(rutaParte)) {
                    listaPartes.push({
                        numero: numeroParte,
                        ruta: rutaParte
                    });
                }
            }

            if (listaPartes.length === 0) {
                console.error("❌ No se pudo generar ninguna parte del video");
                return res.json({
                    status: 'error',
                    mensaje: '❌ Error al cortar el video'
                });
            }

            console.log(`✅ Total de partes válidas generadas: ${listaPartes.length}`);

            // Enviamos a Telegram
            console.log("📤 Enviando partes a los canales...");
            for (const parte of listaPartes) {
                const mensajeTelegram = `🎬 <b>${tituloOriginal}</b>
📌 <b>Parte:</b> ${parte.numero} de ${listaPartes.length}
✅ Contenido procesado automáticamente
🔗 <b>Canal:</b> ${config.CANAL_PUBLICO?.NOMBRE || 'EnseñaEn15'}`;

                try {
                    await enviarADosCanales(parte.ruta, mensajeTelegram, parte.numero);
                    console.log(`✅ Parte ${parte.numero} enviada correctamente`);
                } catch (error) {
                    console.error(`❌ Error al enviar la parte ${parte.numero}:`, error.message);
                }

                // Eliminamos archivo temporal
                if (fs.existsSync(parte.ruta)) {
                    fs.unlinkSync(parte.ruta);
                    console.log(`🗑️ Parte ${parte.numero} eliminada del disco`);
                }

                await new Promise(resolve => setTimeout(resolve, 1500));
            }

            // Eliminamos archivo original
            if (config.BORRAR_ARCHIVOS_DESPUES !== false && fs.existsSync(rutaArchivoOriginal)) {
                fs.unlinkSync(rutaArchivoOriginal);
                console.log("🗑️ Archivo original eliminado");
            }

            console.log("\n✅ ¡PROCESO FINALIZADO CON ÉXITO!");
            return res.json({
                status: 'ok',
                mensaje: '✅ El archivo fue procesado y enviado correctamente'
            });

        } catch (error) {
            console.error("\n❌ ERROR GENERAL AL PROCESAR:", error.message);
            return res.json({
                status: 'error',
                mensaje: `❌ Ocurrió un error: ${error.message}`
            });
        }
    });
});

// ==============================================
// RUTA PARA PROCESAR ENLACES
// ==============================================
app.post('/procesar-enlace', async (req, res) => {
    console.log("\n📥 RECIBIDA SOLICITUD DE PROCESAR ENLACE");
    try {
        const { enlace } = req.body;
        console.log("🔗 Enlace recibido:", enlace);

        if (!enlace || enlace.trim() === '') {
            console.error("❌ Enlace vacío");
            return res.json({
                status: 'error',
                mensaje: '❌ Debes ingresar un enlace válido'
            });
        }

        console.log("⏳ Iniciando procesamiento del enlace...");
        const resultado = await procesarEnlace(enlace.trim());

        if (resultado) {
            console.log("✅ Enlace procesado correctamente");
            return res.json({
                status: 'ok',
                mensaje: '✅ El enlace fue procesado y enviado correctamente'
            });
        } else {
            throw new Error("El procesamiento del enlace devolvió un resultado vacío");
        }

    } catch (error) {
        console.error("\n❌ ERROR AL PROCESAR ENLACE:", error.message);
        return res.json({
            status: 'error',
            mensaje: `❌ Ocurrió un error: ${error.message}`
        });
    }
});

// ==============================================
// FUNCIONES AUXILIARES
// ==============================================
/**
 * Obtiene la duración total de un video
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        execFile('ffprobe', [
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            rutaArchivo
        ], (error, stdout) => {
            if (error || !stdout || isNaN(parseFloat(stdout))) {
                return reject(new Error("No se pudo leer la duración del video"));
            }
            resolve(parseFloat(stdout.trim()));
        });
    });
}

// ==============================================
// INICIAR SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    console.log("\n" + "=".repeat(60));
    console.log(`✅ SERVIDOR INICIADO CORRECTAMENTE`);
    console.log(`🌐 Dirección: http://localhost:${PUERTO}`);
    console.log("=".repeat(60) + "\n");
});

// Capturamos cualquier error
process.on('uncaughtException', (error) => {
    console.error("\n❌ ERROR NO CONTROLADO:", error.message);
});

process.on('unhandledRejection', (error) => {
    console.error("\n❌ PROMESA SIN RESOLVER:", error.message);
});
