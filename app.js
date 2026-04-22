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

// 🎨 Clase para generar los mensajes que se envían a Telegram
class MallyLogger {
    constructor(nombre, total) {
        this.nombre = nombre.trim().toUpperCase();
        this.total = total;
    }

    exito(n) {
        return `🎬 <b>${this.nombre}</b>\n💎 <b>CAPÍTULO:</b> ${n} / ${this.total}\n✅ <i>Contenido Verificado</i>\n🔗 @MallyUmbrae`;
    }
}

// ⚡ Productor: Corta los segmentos y los agrega a la cola
function productor(rutaVideo, totalPartes, log) {
    return new Promise(async (resolve) => {
        for (let n = 1; n <= totalPartes; n++) {
            console.log(`⚡ CORTANDO PARTE ${n}/${totalPartes}`);
            const rutaArchivo = await cortar.extraerSegmento(rutaVideo, n);
            
            if (fs.existsSync(rutaArchivo)) {
                cola.push({
                    n: n,
                    path: rutaArchivo,
                    caption: log.exito(n)
                });
            }
        }
        cola.push(null);
        resolve();
    });
}

// 📤 Consumidor: Envía los archivos mientras se siguen cortando
function consumidor() {
    return new Promise(async (resolve) => {
        while (true) {
            while (cola.length === 0) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            const item = cola.shift();
            if (item === null) break;

            console.log(`📤 ENVIANDO PARTE ${item.n}`);
            const enviado = await enviar.despacharATelegram(item.path, item.caption);
            
            if (enviado) {
                console.log(`✅ PARTE ${item.n} ENVIADA CORRECTAMENTE`);
            }

            if (fs.existsSync(item.path)) {
                fs.unlinkSync(item.path);
            }
        }
        resolve();
    });
}

// 🛠️ CONFIGURACIÓN DE SUBIDA MEJORADA Y MÁS RÁPIDA
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(fileUpload({
    limits: { fileSize: 10 * 1024 * 1024 * 1024 }, // 10GB máximo
    abortOnLimit: false,
    useTempFiles: false, // 🔴 CAMBIO CLAVE: Ya no usamos archivos temporales, recibe directo
    // Escribimos directo a la carpeta final sin pasos intermedios
    createParentPath: true,
    debug: false
}));

// ✅ Carga de archivos estáticos
app.use(express.static(path.join(__dirname, 'templates')));

// 📋 Rutas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/procesar', async (req, res) => {
    if (PROCESANDO) {
        return res.json({ status: "ocupado", mensaje: "⏳ Ya estoy trabajando en otro vídeo, espera un momento..." });
    }

    if (!req.files || !req.files.video) {
        return res.json({ status: "error", mensaje: "❌ Debes seleccionar un archivo de vídeo" });
    }

    const archivo = req.files.video;
    const titulo = req.body.titulo || "SIN TÍTULO";

    // 🔴 AHORA GUARDAMOS DIRECTO EN SU LUGAR FINAL, SIN PASOS INTERMEDIOS
    const rutaEntrada = path.join(INPUT_FOLDER, archivo.name);
    await archivo.mv(rutaEntrada);

    PROCESANDO = true;

    try {
        // 🧮 Cálculo de duración
        const duracion = await new Promise((resolve, reject) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaEntrada
            ], (error, stdout) => {
                if (error) {
                    console.warn("⚠️ No se pudo leer la duración, se usará valor estimado: 5 horas");
                    return resolve(18000);
                }
                const valorLimpio = stdout.trim().replace(/[^0-9.]/g, '');
                const duracionCalculada = parseFloat(valorLimpio) || 18000;
                resolve(duracionCalculada);
            });
        });

        const totalPartes = Math.floor(duracion / config.CLIP_DURATION) + 1;

        res.json({
            status: "ok",
            mensaje: `🚀 PROCESANDO ${totalPartes} PARTES EN MODO LUZ`
        });

        console.log(`🔥 INICIANDO PROCESO: ${titulo} | Duración: ${Math.round(duracion / 60)} minutos | Partes: ${totalPartes}`);
        const log = new MallyLogger(titulo, totalPartes);

        await Promise.all([
            productor(rutaEntrada, totalPartes, log),
            consumidor()
        ]);

        // 🧹 Limpieza final
        if (fs.existsSync(rutaEntrada)) fs.unlinkSync(rutaEntrada);
        
        // Borramos archivos temporales viejos por si quedaron
        if (fs.existsSync(TEMP_UPLOAD_FOLDER)) {
            fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
                const rutaArchivoTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
                fs.unlinkSync(rutaArchivoTemp);
            });
        }

        PROCESANDO = false;
        console.log("✅ ¡MISIÓN COMPLETADA! Todo enviado correctamente");

    } catch (error) {
        PROCESANDO = false;
        console.error("❌ ERROR:", error);
        res.json({ status: "error", mensaje: "❌ Ocurrió un error al procesar el vídeo" });

        if (fs.existsSync(rutaEntrada)) fs.unlinkSync(rutaEntrada);
    }
});

// 🚀 Inicio del servidor
console.log("=".repeat(50));
console.log("⚡ MALLYCUTS - MODO EXPRESS ACTIVADO ⚡");
console.log("🌐 Accedé a: http://localhost:5000");
console.log("⏱️ Cada parte dura:", config.CLIP_DURATION, "segundos");
console.log("=".repeat(50));

app.listen(PORT, '0.0.0.0', () => {});
