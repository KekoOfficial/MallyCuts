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
const cola = [];

// 🎨 Generador de mensajes personalizados
class MallyLogger {
    constructor(nombre, total) {
        this.nombre = nombre.trim().toUpperCase();
        this.total = total;
        this.enlaceCanal = config.CANAL_MIO.NOMBRE;
    }

    obtenerMensaje(n) {
        return `🎬 <b>${this.nombre}</b>
💎 <b>PARTE:</b> ${n} / ${this.total}
✅ <i>Contenido procesado y verificado</i>
🔗 ${this.enlaceCanal}`;
    }
}

// ⚡ Función para cortar los vídeos
function productor(rutaVideo, totalPartes, log) {
    return new Promise(async (resolve) => {
        for (let n = 1; n <= totalPartes; n++) {
            console.log(`\n⚡ PROCESANDO PARTE ${n}/${totalPartes}`);
            const rutaArchivo = await cortar.extraerSegmento(rutaVideo, n);
            
            if (rutaArchivo) {
                cola.push({
                    numero: n,
                    ruta: rutaArchivo,
                    mensaje: log.obtenerMensaje(n)
                });
            }
        }
        cola.push(null);
        resolve();
    });
}

// 📤 Función para enviar los archivos
function consumidor() {
    return new Promise(async (resolve) => {
        while (true) {
            while (cola.length === 0) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }

            const item = cola.shift();
            if (item === null) break;

            console.log(`📤 ENVIANDO PARTE ${item.numero}`);
            const resultadoEnvio = await enviar.despacharATelegram(item.ruta, item.mensaje);
            
            if (resultadoEnvio) {
                console.log(`✅ PARTE ${item.numero} COMPLETADA`);
            } else {
                console.log(`⚠️ PARTE ${item.numero} NO SE PUDO ENVIAR`);
            }

            // Eliminamos archivos temporales
            if (fs.existsSync(item.ruta)) {
                fs.unlinkSync(item.ruta);
            }
        }
        resolve();
    });
}

// 🛠️ Configuración del servidor
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// 🚀 Configuración de subida optimizada para archivos grandes
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
            mensaje: "⏳ Ya estoy trabajando en otro archivo, por favor espera..." 
        });
    }

    if (!req.files || !req.files.video) {
        return res.json({ 
            status: "error", 
            mensaje: "❌ Tenés que seleccionar un archivo de vídeo primero" 
        });
    }

    const archivoRecibido = req.files.video;
    const tituloArchivo = req.body.titulo || "SIN TÍTULO";

    PROCESANDO = true;

    try {
        // Guardamos el archivo recibido
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
                    console.log("⚠️ No se pudo leer la duración exacta, se usará valor estimado de 5 horas");
                    return resolve(18000);
                }
                resolve(parseFloat(stdout.trim()));
            });
        });

        const cantidadPartes = Math.floor(duracionSegundos / config.CLIP_DURATION) + 1;

        // Respondemos al usuario
        res.json({
            status: "ok",
            mensaje: `🚀 PROCESANDO ${cantidadPartes} PARTES`
        });

        // 📋 Información del proceso
        console.log("\n" + "=".repeat(50));
        console.log("📋 DATOS DEL PROCESO");
        console.log(`📌 Título: ${tituloArchivo}`);
        console.log(`⏱️ Duración total: ${Math.round(duracionSegundos / 60)} minutos`);
        console.log(`🔢 Cantidad de partes: ${cantidadPartes}`);
        console.log(`👤 Canal que se muestra: ${config.CANAL_MIO.NOMBRE}`);
        console.log(`🔒 Contenido guardado en: Canal Privado`);
        console.log("=".repeat(50) + "\n");

        // Iniciamos el proceso
        const generadorMensajes = new MallyLogger(tituloArchivo, cantidadPartes);
        await Promise.all([
            productor(rutaArchivoOriginal, cantidadPartes, generadorMensajes),
            consumidor()
        ]);

        // 🧹 Limpieza final
        if (fs.existsSync(rutaArchivoOriginal)) fs.unlinkSync(rutaArchivoOriginal);
        fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });

        PROCESANDO = false;
        console.log("\n✅ ¡TODO FINALIZADO CORRECTAMENTE!");
        console.log("=".repeat(50) + "\n");

    } catch (error) {
        PROCESANDO = false;
        console.error("\n❌ ERROR GENERAL:", error.message);
        res.json({ status: "error", mensaje: "❌ Ocurrió un error al procesar el archivo" });

        // Liberamos archivos si ocurrió un error
        const rutaArchivoOriginal = path.join(INPUT_FOLDER, req.files?.video?.name || "");
        if (fs.existsSync(rutaArchivoOriginal)) fs.unlinkSync(rutaArchivoOriginal);
        
        fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });
    }
});

// 🚀 Iniciar servidor
console.log("==================================================");
console.log("⚡ MALLYCUTS - SISTEMA ACTIVADO");
console.log("🌐 Accedé en tu navegador: http://localhost:5000");
console.log("⏱️ Cada parte dura:", config.CLIP_DURATION, "segundos");
console.log("👤 Canal visible:", config.CANAL_MIO.NOMBRE);
console.log("🔒 Contenido guardado solo en tu canal privado");
console.log("==================================================");

app.listen(PORT, '0.0.0.0', () => {});
