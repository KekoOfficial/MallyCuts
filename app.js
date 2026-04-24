// Importamos las dependencias necesarias
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const config = require('./config');
const { procesarEnlace } = require('./core/descargar');
const { extraerSegmento } = require('./core/cortar');
const { enviarADosCanales } = require('./core/enviar');

// Inicializamos la aplicación
const app = express();
const PUERTO = 3000;

// Configuración general del servidor
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Creamos las carpetas necesarias si no existen
const carpetas = [
    config.ORIGINAL_FOLDER,
    config.PROCESADOS_FOLDER
];

carpetas.forEach(carpeta => {
    if (!fs.existsSync(carpeta)) {
        fs.mkdirSync(carpeta, { recursive: true, mode: 0o777 });
        console.log(`📁 Carpeta creada: ${carpeta}`);
    }
});

// ==============================================
// 📤 CONFIGURACIÓN PARA SUBIDA DE ARCHIVOS
// ==============================================
const almacenamientoArchivos = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, config.ORIGINAL_FOLDER);
    },
    filename: (req, file, cb) => {
        // Limpiamos el título para que no tenga caracteres que den problemas
        let tituloArchivo = req.body.titulo.trim() || 'video_sin_titulo';
        tituloArchivo = tituloArchivo.replace(/[<>:"/\\|?*\n\r]/g, ' ').substring(0, 100);
        const nombreFinal = `${tituloArchivo}_${Date.now()}.mp4`;
        cb(null, nombreFinal);
    }
});

// Filtro para aceptar solo archivos de video
const filtroArchivos = (req, file, cb) => {
    const tiposPermitidos = ['video/mp4', 'video/mkv', 'video/avi', 'video/mov'];
    if (tiposPermitidos.includes(file.mimetype)) {
        cb(null, true);
    } else {
        cb(new Error('Solo se permiten archivos de video'), false);
    }
};

// Configuración final de multer
const subirArchivo = multer({
    storage: almacenamientoArchivos,
    fileFilter: filtroArchivos,
    limits: {
        fileSize: 500 * 1024 * 1024 // Límite de 500MB por archivo
    }
});

// ==============================================
// 📥 RUTA PARA PROCESAR ARCHIVOS SUBIDOS
// ==============================================
app.post('/procesar', subirArchivo.single('video'), async (req, res) => {
    try {
        // Verificamos que tengamos los datos necesarios
        if (!req.body.titulo || !req.file) {
            return res.json({
                status: 'error',
                mensaje: '❌ Debes ingresar un título y seleccionar un archivo de video'
            });
        }

        console.log("\n" + "=".repeat(60));
        console.log("📤 PROCESANDO ARCHIVO SUBIDO");
        console.log(`📝 Título: ${req.body.titulo}`);
        console.log(`📂 Archivo: ${req.file.filename}`);
        console.log("=".repeat(60));

        // Datos del archivo
        const tituloOriginal = req.body.titulo.trim();
        const rutaArchivoOriginal = path.join(config.ORIGINAL_FOLDER, req.file.filename);

        // Verificamos que el archivo se haya guardado correctamente
        if (!fs.existsSync(rutaArchivoOriginal)) {
            return res.json({
                status: 'error',
                mensaje: '❌ No se pudo guardar el archivo, intenta nuevamente'
            });
        }

        // Obtenemos la duración del video para calcular las partes
        const duracionTotal = await obtenerDuracionVideo(rutaArchivoOriginal);
        const cantidadPartes = Math.floor(duracionTotal / config.CLIP_DURATION) + 1;

        console.log(`⏱️ Duración total: ${Math.round(duracionTotal)} segundos`);
        console.log(`✂️ Se generarán ${cantidadPartes} partes de ${config.CLIP_DURATION} segundos cada una`);

        // Procesamos y cortamos todas las partes
        const listaPartes = [];
        for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
            console.log(`🔄 Procesando parte ${numeroParte}/${cantidadPartes}`);
            
            const rutaParte = await extraerSegmento(rutaArchivoOriginal, numeroParte, tituloOriginal);
            
            if (rutaParte && fs.existsSync(rutaParte)) {
                listaPartes.push({
                    numero: numeroParte,
                    ruta: rutaParte
                });
            }
        }

        console.log(`✅ Se generaron correctamente ${listaPartes.length} partes`);

        // Enviamos todas las partes a los canales de Telegram
        console.log("\n📤 ENVIANDO CONTENIDO A LOS CANALES");
        for (const parte of listaPartes) {
            const mensajeTelegram = `🎬 <b>${tituloOriginal}</b>
📌 <b>Parte:</b> ${parte.numero} de ${listaPartes.length}
✅ Contenido procesado automáticamente
🔗 <b>Canal:</b> ${config.CANAL_PUBLICO.NOMBRE}`;

            const enviado = await enviarADosCanales(parte.ruta, mensajeTelegram, parte.numero);
            
            // Eliminamos el archivo después de enviarlo para liberar espacio
            if (fs.existsSync(parte.ruta)) {
                fs.unlinkSync(parte.ruta);
            }

            // Pequeña pausa para no saturar la API
            await new Promise(resolve => setTimeout(resolve, 1500));
        }

        // Eliminamos el archivo original si está configurado así
        if (config.BORRAR_ARCHIVOS_DESPUES && fs.existsSync(rutaArchivoOriginal)) {
            fs.unlinkSync(rutaArchivoOriginal);
            console.log("🗑️ Archivo original eliminado");
        }

        console.log("\n" + "=".repeat(60));
        console.log("✅ ¡PROCESO FINALIZADO CON ÉXITO!");
        console.log("=".repeat(60) + "\n");

        // Respondemos al navegador que todo salió bien
        return res.json({
            status: 'ok',
            mensaje: '✅ El archivo fue procesado y enviado correctamente'
        });

    } catch (error) {
        console.error("\n❌ ERROR AL PROCESAR ARCHIVO:", error.message);
        return res.json({
            status: 'error',
            mensaje: '❌ Ocurrió un error al procesar el archivo, revisa los datos e intenta de nuevo'
        });
    }
});

// ==============================================
// 🔗 RUTA PARA PROCESAR ENLACES
// ==============================================
app.post('/procesar-enlace', async (req, res) => {
    try {
        const { enlace } = req.body;

        if (!enlace || enlace.trim() === '') {
            return res.json({
                status: 'error',
                mensaje: '❌ Debes ingresar un enlace válido'
            });
        }

        console.log("\n" + "=".repeat(60));
        console.log("🔗 PROCESANDO ENLACE RECIBIDO");
        console.log(`🌐 Enlace: ${enlace}`);
        console.log("=".repeat(60));

        // Ejecutamos la función que descarga, corta y envía el contenido
        const resultado = await procesarEnlace(enlace.trim());

        if (resultado) {
            console.log("\n✅ ¡ENLACE PROCESADO CON ÉXITO!");
            return res.json({
                status: 'ok',
                mensaje: '✅ El enlace fue procesado y enviado correctamente'
            });
        } else {
            throw new Error("No se pudo completar el procesamiento del enlace");
        }

    } catch (error) {
        console.error("\n❌ ERROR AL PROCESAR ENLACE:", error.message);
        return res.json({
            status: 'error',
            mensaje: '❌ Ocurrió un error al procesar el enlace, revisa que sea válido e intenta de nuevo'
        });
    }
});

// ==============================================
// 🛠️ FUNCIONES AUXILIARES
// ==============================================
/**
 * Obtiene la duración total de un video en segundos
 * @param {string} rutaArchivo - Ruta completa del archivo de video
 * @returns {Promise<number>} Duración en segundos
 */
function obtenerDuracionVideo(rutaArchivo) {
    return new Promise((resolve, reject) => {
        const { execFile } = require('child_process');
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
// 🚀 INICIAMOS EL SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    console.log("\n" + "=".repeat(60));
    console.log(`✅ SERVIDOR INICIADO CORRECTAMENTE`);
    console.log(`🌐 Accede en: http://localhost:${PUERTO}`);
    console.log(`📂 Carpeta del proyecto: ${__dirname}`);
    console.log("=".repeat(60) + "\n");
});

// Manejo de errores globales
process.on('uncaughtException', (error) => {
    console.error("\n❌ ERROR GLOBAL:", error.message);
});

process.on('unhandledRejection', (error) => {
    console.error("\n❌ PROMESA NO RESUELTA:", error.message);
});
