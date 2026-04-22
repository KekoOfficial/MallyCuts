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
fs.mkdirSync(INPUT_FOLDER, { recursive: true });
fs.mkdirSync(config.TEMP_FOLDER, { recursive: true });

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
            
            // Llamamos a la función que corta el vídeo
            const rutaArchivo = await cortar.extraerSegmento(rutaVideo, n);
            
            if (fs.existsSync(rutaArchivo)) {
                // Agregamos a la cola para que se envíe
                cola.push({
                    n: n,
                    path: rutaArchivo,
                    caption: log.exito(n)
                });
            }
        }
        // Marcamos que terminó de agregar todos los elementos
        cola.push(null);
        resolve();
    });
}

// 📤 Consumidor: Envía los archivos mientras se siguen cortando
function consumidor() {
    return new Promise(async (resolve) => {
        while (true) {
            // Esperamos hasta que haya archivos en la cola
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

            // Eliminamos el archivo temporal después de enviarlo
            if (fs.existsSync(item.path)) {
                fs.unlinkSync(item.path);
            }
        }
        resolve();
    });
}

// 🛠️ Configuración de Express
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(fileUpload({
    limits: { fileSize: 1024 * 1024 * 1024 * 10 }, // Límite de 10GB por archivo, suficiente para vídeos muy largos
    abortOnLimit: false,
    useTempFiles: true,
    tempFileDir: '/tmp/'
}));

// ✅ Permite cargar archivos estáticos (CSS, imágenes, etc.) de la carpeta templates
app.use(express.static(path.join(__dirname, 'templates')));

// 📋 Rutas del sistema
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

    // Guardamos el archivo subido en la carpeta de entrada
    const rutaEntrada = path.join(INPUT_FOLDER, archivo.name);
    await archivo.mv(rutaEntrada);

    PROCESANDO = true;

    try {
        // 🧮 Calculamos la duración total del vídeo y la cantidad de partes
        // Método mejorado que funciona incluso con vídeos de muchas horas
        const duracion = await new Promise((resolve, reject) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaEntrada
            ], (error, stdout) => {
                if (error) {
                    console.warn("⚠️ No se pudo leer la duración, se usará el valor estimado:", error.message);
                    // Si falla, calculamos aproximadamente: 5 horas = 18000 segundos
                    return resolve(18000);
                }
                // Convertimos el valor a número, limpiamos espacios y caracteres extraños
                const valorLimpio = stdout.trim().replace(/[^0-9.]/g, '');
                const duracionCalculada = parseFloat(valorLimpio) || 18000;
                resolve(duracionCalculada);
            });
        });

        // Calculamos cuántas partes se van a generar
        const totalPartes = Math.floor(duracion / config.CLIP_DURATION) + 1;

        // Enviamos la respuesta al usuario de inmediato
        res.json({
            status: "ok",
            mensaje: `🚀 PROCESANDO ${totalPartes} PARTES EN MODO LUZ`
        });

        // 🚀 Iniciamos los procesos en paralelo: cortar y enviar al mismo tiempo
        console.log(`🔥 INICIANDO PROCESO: ${titulo} | DURACIÓN: ${Math.round(duracion / 60)} minutos | CANTIDAD DE PARTES: ${totalPartes}`);
        const log = new MallyLogger(titulo, totalPartes);

        await Promise.all([
            productor(rutaEntrada, totalPartes, log),
            consumidor()
        ]);

        // 🧹 Limpiamos el archivo original después de terminar todo
        if (fs.existsSync(rutaEntrada)) {
            fs.unlinkSync(rutaEntrada);
            console.log(`🗑️ Archivo original eliminado`);
        }

        PROCESANDO = false;
        console.log("✅ ¡MISIÓN COMPLETADA! Todo el contenido se envió correctamente");

    } catch (error) {
        PROCESANDO = false;
        console.error("❌ ERROR EN EL PROCESO:", error);
        res.json({ status: "error", mensaje: "❌ Ocurrió un error al procesar el vídeo" });

        // En caso de error, liberamos el archivo si se había guardado
        if (fs.existsSync(rutaEntrada)) {
            fs.unlinkSync(rutaEntrada);
        }
    }
});

// 🚀 Iniciamos el servidor
console.log("=".repeat(50));
console.log("⚡ MALLYCUTS - MODO EXPRESS ACTIVADO ⚡");
console.log("🌐 Accedé desde tu navegador a: http://localhost:5000");
console.log("⏱️ Cada parte dura:", config.CLIP_DURATION, "segundos");
console.log("=".repeat(50));

app.listen(PORT, '0.0.0.0', () => {});
