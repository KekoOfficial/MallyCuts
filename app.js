const express = require('express');
const path = require('path');
const fs = require('fs');
const fileUpload = require('express-fileupload');
const config = require('./config');
const { extraerSegmento } = require('./core/cortar');
const { enviarADosCanales } = require('./core/enviar');
const { procesarEnlace } = require('./core/descargar');

// Inicializamos la aplicación
const app = express();
const PUERTO = 3000;

// Configuración básica
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(fileUpload({
    createParentPath: true,
    limits: { fileSize: 500 * 1024 * 1024 }, // Hasta 500MB por archivo
    abortOnLimit: true,
    responseOnLimit: "El archivo es demasiado grande, el límite es 500MB"
}));

// Carpeta pública para archivos estáticos (CSS, imágenes, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// Ruta principal: Carga la página web
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// ==============================================
// 📤 RUTA 1: PROCESAR ARCHIVO SUBIDO DESDE LA WEB
// ==============================================
app.post('/procesar', async (req, res) => {
    try {
        // Obtenemos los datos enviados
        const titulo = req.body.titulo?.trim();
        const archivoVideo = req.files?.video;

        // Verificamos que tengamos los datos necesarios
        if (!titulo) {
            return res.json({ status: "error", mensaje: "Falta el título del contenido" });
        }

        if (!archivoVideo) {
            return res.json({ status: "error", mensaje: "No se recibió ningún archivo de video" });
        }

        console.log("\n" + "=".repeat(60));
        console.log("📥 NUEVO CONTENIDO RECIBIDO DESDE LA WEB");
        console.log(`📝 Título: ${titulo}`);
        console.log(`📹 Archivo: ${archivoVideo.name} | Tamaño: ${(archivoVideo.size / 1024 / 1024).toFixed(2)} MB`);
        console.log("=".repeat(60));

        // Guardamos el archivo original en la carpeta correspondiente
        const nombreArchivoLimpio = titulo.replace(/[<>:"/\\|?*\n\r]/g, ' ').trim().substring(0, 100);
        const rutaOriginal = path.join(config.ORIGINAL_FOLDER, `${nombreArchivoLimpio}.mp4`);
        
        await archivoVideo.mv(rutaOriginal);
        console.log("✅ Archivo guardado correctamente");

        // PASO 1: Obtener duración y calcular cantidad de partes
        const duracionTotal = await obtenerDuracionVideo(rutaOriginal);
        const cantidadPartes = Math.floor(duracionTotal / config.CLIP_DURATION) + 1;
        console.log(`ℹ️ Duración total: ${Math.round(duracionTotal)} segundos | Se generarán ${cantidadPartes} partes de ${config.CLIP_DURATION} segundos`);

        // PASO 2: Generar todas las partes con tus ajustes
        console.log("\n✂️ Iniciando corte y procesamiento...");
        const listaPartes = [];

        for (let numeroParte = 1; numeroParte <= cantidadPartes; numeroParte++) {
            console.log(`🔄 Procesando parte ${numeroParte}/${cantidadPartes}`);
            const rutaParte = await extraerSegmento(rutaOriginal, numeroParte);
            
            if (rutaParte) {
                listaPartes.push({
                    numero: numeroParte,
                    ruta: rutaParte
                });
            }
        }

        console.log(`✅ Se generaron ${listaPartes.length} partes válidas`);

        // PASO 3: Enviar todas las partes a los dos canales
        console.log("\n📤 Enviando contenido a los canales...");
        for (const parte of listaPartes) {
            const mensaje = `🎬 <b>${titulo}</b>
📌 <b>Parte:</b> ${parte.numero} de ${listaPartes.length}
✅ Contenido procesado
🔗 <b>Canal:</b> ${config.CANAL_PUBLICO.NOMBRE}`;

            // Enviamos usando tu función que ya funciona
            await enviarADosCanales(parte.ruta, mensaje, parte.numero);

            // Eliminamos la parte ya enviada
            if (fs.existsSync(parte.ruta)) {
                fs.unlinkSync(parte.ruta);
            }

            // Pequeña pausa para no saturar
            await new Promise(resolve => setTimeout(resolve, 1200));
        }

        // PASO 4: Limpieza final
        if (config.BORRAR_ARCHIVOS_DESPUES && fs.existsSync(rutaOriginal)) {
            fs.unlinkSync(rutaOriginal);
            console.log("🗑️ Archivo original eliminado");
        }

        console.log("\n✅ ¡PROCESO FINALIZADO CON ÉXITO!");
        console.log("=".repeat(60) + "\n");

        res.json({ status: "ok", mensaje: "Todo procesado y enviado correctamente" });

    } catch (error) {
        console.error("\n❌ ERROR EN EL PROCESO:", error.message);
        res.json({ status: "error", mensaje: `Ocurrió un error: ${error.message}` });
    }
});

// ==============================================
// 🔗 RUTA 2: PROCESAR ENLACE DE VIDEO
// ==============================================
app.post('/procesar-enlace', async (req, res) => {
    try {
        const { enlace } = req.body;

        if (!enlace || enlace.trim() === "") {
            return res.json({ status: "error", mensaje: "Por favor ingresá un enlace válido" });
        }

        console.log("\n" + "=".repeat(60));
        console.log("🔗 NUEVO ENLACE RECIBIDO");
        console.log(`🌐 Enlace: ${enlace}`);
        console.log("=".repeat(60));

        // Llamamos a la función que hace todo el proceso automático
        const resultado = await procesarEnlace(enlace.trim());

        if (resultado) {
            res.json({ status: "ok", mensaje: "El contenido se está procesando y enviando correctamente" });
        } else {
            res.json({ status: "error", mensaje: "No se pudo procesar el enlace, revisá que sea válido" });
        }

    } catch (error) {
        console.error("\n❌ ERROR AL PROCESAR ENLACE:", error.message);
        res.json({ status: "error", mensaje: `Error: ${error.message}` });
    }
});

// ==============================================
// 🛠️ FUNCIONES AUXILIARES
// ==============================================
/**
 * Obtiene la duración de un video en segundos
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
// 🚀 INICIAR EL SERVIDOR
// ==============================================
app.listen(PUERTO, () => {
    console.log("\n" + "=".repeat(60));
    console.log(`✅ SERVIDOR INICIADO CORRECTAMENTE`);
    console.log(`🌐 Accedé desde: http://localhost:${PUERTO}`);
    console.log(`⚙️ Sistema: MallyCuts`);
    console.log(`📢 Canal público: ${config.CANAL_PUBLICO.NOMBRE}`);
    console.log(`🔒 Canal privado: Solo acceso autorizado`);
    console.log("=".repeat(60) + "\n");
});
