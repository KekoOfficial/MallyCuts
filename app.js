const express = require('express');
const path = require('path');
const { execFile } = require('child_process');
const fs = require('fs');
const fileUpload = require('express-fileupload');
const cortar = require('./core/cortar');
const enviar = require('./core/enviar');
const config = require('./config');

const app = express();
const PORT = 5000;

// 📂 Carpetas de trabajo
const INPUT_FOLDER = path.join(__dirname, 'videos', 'input');
const TEMP_UPLOAD_FOLDER = path.join(__dirname, 'temp_uploads');
fs.mkdirSync(INPUT_FOLDER, { recursive: true });
fs.mkdirSync(config.TEMP_FOLDER, { recursive: true });
fs.mkdirSync(TEMP_UPLOAD_FOLDER, { recursive: true });

// ⚙️ Variables de control
let PROCESANDO = false;
const listaDePartes = []; // Aquí guardaremos todas las partes después de cortar

// 🎨 Generador de mensajes personalizados
class GeneradorMensajes {
    constructor(nombreContenido, totalPartes) {
        this.nombreContenido = nombreContenido.trim().toUpperCase();
        this.totalPartes = totalPartes;
        this.nombreCanalPublico = config.CANAL_PUBLICO.NOMBRE;
    }

    obtenerMensajeParte(numeroParte) {
        return `🎬 <b>${this.nombreContenido}</b>
📌 <b>Parte:</b> ${numeroParte} de ${this.totalPartes}
✅ Contenido procesado y verificado
🔗 <b>Canal:</b> ${this.nombreCanalPublico}`;
    }
}

// ⚡ PASO 1: CORTAR TODO EL VÍDEO Y GENERAR TODAS LAS PARTES
async function cortarTodoElVideo(rutaVideo, totalPartes) {
    console.log("\n" + "=".repeat(60));
    console.log("🔪 INICIANDO CORTE DE TODO EL CONTENIDO...");
    console.log("=".repeat(60));

    for (let numeroParte = 1; numeroParte <= totalPartes; numeroParte++) {
        console.log(`\n🔪 Cortando parte ${numeroParte}/${totalPartes}`);
        const rutaParte = await cortar.extraerSegmento(rutaVideo, numeroParte);
        
        if (rutaParte) {
            listaDePartes.push({
                numero: numeroParte,
                ruta: rutaParte
            });
        }
    }

    console.log("\n" + "=".repeat(60));
    console.log(`✅ CORTE FINALIZADO: Se generaron ${listaDePartes.length} partes correctamente`);
    console.log("=".repeat(60) + "\n");
}

// 📤 PASO 2: ENVIAR DE A UNA PARTE A LOS DOS CANALES
async function enviarTodasLasPartes(generadorMensajes) {
    console.log("\n" + "=".repeat(60));
    console.log("📤 INICIANDO ENVÍO DE PARTES A LOS DOS CANALES...");
    console.log("=".repeat(60));

    // Recorremos la lista de partes UNA POR UNA
    for (const parte of listaDePartes) {
        const mensaje = generadorMensajes.obtenerMensajeParte(parte.numero);
        
        // Enviamos esta parte a los dos canales
        await enviar.enviarADosCanales(parte.ruta, mensaje, parte.numero);

        // Eliminamos el archivo temporal después de enviarlo
        if (fs.existsSync(parte.ruta)) {
            fs.unlinkSync(parte.ruta);
        }

        // Pequeña pausa entre partes para que todo se sincronice bien
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    console.log("\n" + "=".repeat(60));
    console.log("✅ TODAS LAS PARTES FUERON PROCESADAS Y ENVIADAS");
    console.log("=".repeat(60) + "\n");
}

// 🛠️ Configuración del servidor
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// Configuración de subida de archivos
app.use(fileUpload({
    limits: { fileSize: 10 * 1024 * 1024 * 1024 },
    abortOnLimit: false,
    useTempFiles: true,
    tempFileDir: TEMP_UPLOAD_FOLDER,
    safeFileNames: true,
    preserveExtension: true,
    debug: false,
    createParentPath: true
}));

// Archivos estáticos
app.use(express.static(path.join(__dirname, 'templates')));

// 📋 Rutas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/procesar', async (req, res) => {
    if (PROCESANDO) {
        return res.json({ 
            status: "ocupado", 
            mensaje: "⏳ Ya estoy procesando otro contenido, por favor esperá..." 
        });
    }

    if (!req.files || !req.files.video) {
        return res.json({ 
            status: "error", 
            mensaje: "❌ Tenés que seleccionar un archivo de vídeo primero" 
        });
    }

    const archivoRecibido = req.files.video;
    const nombreContenido = req.body.titulo || "SIN NOMBRE";

    PROCESANDO = true;
    listaDePartes.length = 0; // Limpiamos la lista de partes anteriores

    try {
        // Guardamos el archivo original
        const rutaArchivoOriginal = path.join(INPUT_FOLDER, archivoRecibido.name);
        await archivoRecibido.mv(rutaArchivoOriginal);

        // 🧮 Calculamos duración y cantidad de partes
        const duracionSegundos = await new Promise((resolve) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaArchivoOriginal
            ], (error, stdout) => {
                if (error || !stdout || isNaN(parseFloat(stdout))) {
                    console.log("⚠️ No se pudo leer la duración exacta, se usará valor estimado");
                    return resolve(10);
                }
                resolve(parseFloat(stdout.trim()));
            });
        });

        const cantidadPartes = Math.floor(duracionSegundos / config.CLIP_DURATION) + 1;

        // Respondemos al usuario
        res.json({
            status: "ok",
            mensaje: `🚀 Iniciando proceso: se generarán ${cantidadPartes} partes`
        });

        // 📋 Mostramos información en consola
        console.log("\n" + "=".repeat(60));
        console.log("📋 DATOS DEL PROCESO");
        console.log(`📌 Contenido: ${nombreContenido}`);
        console.log(`⏱️ Duración total: ${Math.round(duracionSegundos)} segundos`);
        console.log(`🔢 Cantidad de partes: ${cantidadPartes}`);
        console.log(`📢 Canal Público: ${config.CANAL_PUBLICO.NOMBRE}`);
        console.log(`🔒 Canal Privado: Solo vos`);
        console.log("=".repeat(60) + "\n");

        // 🚀 PASOS DEL PROCESO EN ORDEN:
        // 1. Cortar TODO el vídeo primero
        await cortarTodoElVideo(rutaArchivoOriginal, cantidadPartes);

        // 2. Preparar mensajes
        const generadorMensajes = new GeneradorMensajes(nombreContenido, cantidadPartes);

        // 3. Enviar de a una
