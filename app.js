const express = require('express');
const fs = require('fs');
const path = require('path');
const { execFile } = require('child_process');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const cortar = require('./core/cortar');
const enviar = require('./core/enviar');
const config = require('./config');

const app = express();
const PORT = 5000;

// Carpetas
const INPUT_FOLDER = path.join(__dirname, 'videos', 'input');
fs.mkdirSync(INPUT_FOLDER, { recursive: true });
fs.mkdirSync(config.TEMP_FOLDER, { recursive: true });

// Variables de control
let PROCESANDO = false;
const cola = []; // Usamos array como cola, más rápido que estructuras complejas

// 🎨 Clase para generar mensajes
class MallyLogger {
    constructor(nombre, total) {
        this.nombre = nombre.trim().toUpperCase();
        this.total = total;
    }

    exito(n) {
        return `🎬 <b>${this.nombre}</b>\n💎 <b>CAPÍTULO:</b> ${n} / ${this.total}\n✅ <i>Contenido Verificado</i>\n🔗 @MallyUmbrae`;
    }
}

// ⚡ Productor: Corta y agrega a la cola
function productor(rutaVideo, totalPartes, log) {
    return new Promise(async (resolve) => {
        for (let n = 1; n <= totalPartes; n++) {
            console.log(`⚡ CORTANDO PARTE ${n}/${totalPartes}`);
            
            // Cortar el segmento
            const rutaArchivo = await cortar.extraerSegmento(rutaVideo, n);
            
            if (fs.existsSync(rutaArchivo)) {
                // Agregar a la cola para ser enviado
                cola.push({
                    n: n,
                    path: rutaArchivo,
                    caption: log.exito(n)
                });
            }
        }
        // Marcar fin de elementos
        cola.push(null);
        resolve();
    });
}

// 📤 Consumidor: Envía mientras se siguen cortando
function consumidor() {
    return new Promise(async (resolve) => {
        while (true) {
            // Esperar hasta que haya elementos en la cola
            while (cola.length === 0) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            const item = cola.shift();
            if (item === null) break;

            console.log(`📤 ENVIANDO PARTE ${item.n}`);
            
            const enviado = await enviar.despacharATelegram(item.path, item.caption);
            
            if (enviado) {
                console.log(`✅ PARTE ${item.n} ENVIADA`);
            }

            // Eliminar archivo después de enviarlo
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
app.use(express.static(path.join(__dirname, 'templates')));

// 📋 Rutas
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/procesar', async (req, res) => {
    if (PROCESANDO) {
        return res.json({ status: "ocupado", mensaje: "⏳ Ya estoy trabajando..." });
    }

    if (!req.files || !req.files.video) {
        return res.json({ status: "error", mensaje: "Selecciona un video" });
    }

    const archivo = req.files.video;
    const titulo = req.body.titulo || "SIN TITULO";

    // Guardar archivo subido
    const rutaEntrada = path.join(INPUT_FOLDER, archivo.name);
    await archivo.mv(rutaEntrada);

    PROCESANDO = true;

    try {
        // 🧮 Calcular duración y cantidad de partes
        const duracion = await new Promise((resolve, reject) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaEntrada
            ], (error, stdout) => {
                if (error) return reject(error);
                resolve(parseFloat(stdout));
            });
        });

        const totalPartes = Math.floor(duracion / config.CLIP_DURATION) + 1;

        // Enviar respuesta inmediata
        res.json({
            status: "ok",
            mensaje: `🚀 PROCESANDO ${totalPartes} PARTES EN MODO LUZ`
        });

        // 🚀 Iniciar proceso en paralelo
        console.log(`🔥 INICIANDO: ${titulo} | PARTES: ${totalPartes}`);
        const log = new MallyLogger(titulo, totalPartes);

        // Ejecutar al mismo tiempo
        await Promise.all([
            productor(rutaEntrada, totalPartes, log),
            consumidor()
        ]);

        // 🧹 Limpieza final
        if (fs.existsSync(rutaEntrada)) {
            fs.unlinkSync(rutaEntrada);
        }

        PROCESANDO = false;
        console.log("✅ MISION COMPLETADA");

    } catch (error) {
        PROCESANDO = false;
        console.error("❌ ERROR EN EL PROCESO:", error);
        res.json({ status: "error", mensaje: "Ocurrió un error al procesar el vídeo" });
    }
});

// 🚀 Iniciar servidor
console.log("⚡ MALLYCUTS - MODO EXPRESS ACTIVADO ⚡");
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🌐 Servidor activo en http://localhost:${PORT}`);
});
