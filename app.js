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

// 🎨 Clase para generar mensajes (ahora muestra siempre tu canal)
class MallyLogger {
    constructor(nombre, total) {
        this.nombre = nombre.trim().toUpperCase();
        this.total = total;
        // Usamos el nombre de tu canal que configuraste
        this.canalMio = config.CANAL_MIO.NOMBRE;
    }

    exito(n) {
        return `🎬 <b>${this.nombre}</b>\n💎 <b>CAPÍTULO:</b> ${n} / ${this.total}\n✅ <i>Contenido Verificado</i>\n🔗 ${this.canalMio}`;
    }
}

// ⚡ Cortar vídeos
function productor(rutaVideo, totalPartes, log) {
    return new Promise(async (resolve) => {
        for (let n = 1; n <= totalPartes; n++) {
            console.log(`⚡ CORTANDO PARTE ${n}/${totalPartes}`);
            const rutaArchivo = await cortar.extraerSegmento(rutaVideo, n);
            
            if (rutaArchivo && fs.existsSync(rutaArchivo)) {
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

// 📤 Enviar archivos
function consumidor() {
    return new Promise(async (resolve) => {
        while (true) {
            while (cola.length === 0) {
                await new Promise(resolve => setTimeout(resolve, 200));
            }

            const item = cola.shift();
            if (item === null) break;

            console.log(`📤 ENVIANDO PARTE ${item.n}`);
            const enviado = await enviar.despacharATelegram(item.path, item.caption);
            
            if (enviado) {
                console.log(`✅ PARTE ${item.n} GUARDADA CON ÉXITO`);
            } else {
                console.log(`⚠️ Hubo problemas al guardar la parte ${item.n}`);
            }

            if (fs.existsSync(item.path)) {
                fs.unlinkSync(item.path);
            }
        }
        resolve();
    });
}

// 🛠️ CONFIGURACIÓN OPTIMIZADA PARA TERMUX
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Configuración de subida estable
app.use(fileUpload({
    limits: { fileSize: 10 * 1024 * 1024 * 1024 },
    abortOnLimit: false,
    useTempFiles: true,
    tempFileDir: TEMP_UPLOAD_FOLDER,
    safeFileNames: true,
    preserveExtension: true,
    debug: false
}));

// Archivos estáticos
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

    PROCESANDO = true;

    try {
        // Guardar archivo
        const rutaEntrada = path.join(INPUT_FOLDER, archivo.name);
        await archivo.mv(rutaEntrada);

        // Calcular duración
        const duracion = await new Promise((resolve) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaEntrada
            ], (error, stdout) => {
                if (error || !stdout || isNaN(parseFloat(stdout))) {
                    console.log("⚠️ No se pudo leer duración, se usará valor de 5 horas");
                    return resolve(18000);
                }
                resolve(parseFloat(stdout.trim()));
            });
        });

        const totalPartes = Math.floor(duracion / config.CLIP_DURATION) + 1;

        // Responder al usuario
        res.json({
            status: "ok",
            mensaje: `🚀 PROCESANDO ${totalPartes} PARTES EN MODO LUZ`
        });

        console.log(`\n🔥 PROCESO INICIADO`);
        console.log(`📌 Título: ${titulo}`);
        console.log(`⏱️ Duración total: ${Math.round(duracion / 60)} minutos`);
        console.log(`🔢 Cantidad de partes: ${totalPartes}`);
        console.log(`👤 Canal que se muestra: ${config.CANAL_MIO.NOMBRE}`);
        console.log(`🔒 Canal donde se guarda el contenido: Canal Privado\n`);

        // Ejecutar tareas
        const log = new MallyLogger(titulo, totalPartes);
        await Promise.all([productor(rutaEntrada, totalPartes, log), consumidor()]);

        // Limpieza
        if (fs.existsSync(rutaEntrada)) fs.unlinkSync(rutaEntrada);
        fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });

        PROCESANDO = false;
        console.log("\n✅ ¡TODO FINALIZADO CORRECTAMENTE! Todo guardado en tu canal privado\n");

    } catch (error) {
        PROCESANDO = false;
        console.error("\n❌ ERROR EN EL PROCESO:", error.message);
        res.json({ status: "error", mensaje: "❌ Ocurrió un error al procesar el archivo" });

        // Liberar archivos
        const rutaEntrada = path.join(INPUT_FOLDER, req.files?.video?.name || "");
        if (fs.existsSync(rutaEntrada)) fs.unlinkSync(rutaEntrada);
        
        fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });
    }
});

// 🚀 Iniciar servidor
console.log("==================================================");
console.log("⚡ MALLYCUTS - MODO EXPRESS ACTIVADO");
console.log("🌐 Accedé en tu navegador: http://localhost:5000");
console.log("⏱️ Cada parte dura:", config.CLIP_DURATION, "segundos");
console.log("👤 Canal público que se muestra:", config.CANAL_MIO.NOMBRE);
console.log("🔒 Contenido guardado solo en tu canal privado");
console.log("==================================================");

app.listen(PORT, '0.0.0.0', () => {});
