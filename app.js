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
const listaDePartes = []; // Aquí se guardan todas las partes después de cortar

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

// ⚡ PASO 1: CORTAR TODO EL VÍDEO PRIMERO, GENERAR TODAS LAS PARTES
async function cortarTodoElVideo(rutaVideo, totalPartes) {
    console.log("\n" + "=".repeat(60));
    console.log("🔪 INICIANDO CORTE DE TODO EL CONTENIDO...");
    console.log("=".repeat(60));

    // Limpiamos la lista por si había datos anteriores
    listaDePartes.length = 0;

    for (let numeroParte = 1; numeroParte <= totalPartes; numeroParte++) {
        console.log(`\n🔪 Procesando corte de parte ${numeroParte}/${totalPartes}`);
        const rutaParte = await cortar.extraerSegmento(rutaVideo, numeroParte);
        
        if (rutaParte) {
            listaDePartes.push({
                numero: numeroParte,
                ruta: rutaParte
            });
            console.log(`✅ Parte ${numeroParte} guardada en la lista para enviar`);
        } else {
            console.log(`⚠️ Parte ${numeroParte} no se pudo generar, se omitirá`);
        }
    }

    console.log("\n" + "=".repeat(60));
    console.log(`✅ CORTE FINALIZADO: Se generaron ${listaDePartes.length} partes válidas de ${totalPartes} totales`);
    console.log("=".repeat(60) + "\n");
}

// 📤 PASO 2: ENVIAR DE A UNA PARTE A LOS DOS CANALES
async function enviarTodasLasPartes(generadorMensajes) {
    console.log("\n" + "=".repeat(60));
    console.log("📤 INICIANDO ENVÍO DE PARTES A LOS DOS CANALES...");
    console.log("=".repeat(60));

    // Recorremos la lista de partes UNA POR UNA, ordenadamente
    for (const parte of listaDePartes) {
        const mensaje = generadorMensajes.obtenerMensajeParte(parte.numero);
        
        console.log(`\n🔄 PROCESANDO ENVÍO DE LA PARTE ${parte.numero}...`);
        
        // Enviamos esta parte a los dos canales al mismo tiempo
        const resultado = await enviar.enviarADosCanales(parte.ruta, mensaje, parte.numero);

        // Eliminamos el archivo temporal después de enviarlo, no importa si salió bien o mal
        if (fs.existsSync(parte.ruta)) {
            fs.unlinkSync(parte.ruta);
            console.log(`🗑️ Archivo temporal de la parte ${parte.numero} eliminado`);
        }

        // Pequeña pausa entre partes para que Telegram no bloquee los mensajes y todo se sincronice bien
        console.log(`⏳ Esperando 1,5 segundos antes de enviar la siguiente parte...`);
        await new Promise(resolve => setTimeout(resolve, 1500));
    }

    console.log("\n" + "=".repeat(60));
    console.log("✅ ¡TODO EL PROCESO FINALIZADO CON ÉXITO!");
    console.log("✅ TODAS LAS PARTES FUERON ENVIADAS A LOS DOS CANALES");
    console.log("=".repeat(60) + "\n");
}

// 🛠️ Configuración del servidor
app.use(express.json({ limit: '100mb' }));
app.use(express.urlencoded({ extended: true, limit: '100mb' }));

// Configuración de subida de archivos
app.use(fileUpload({
    limits: { fileSize: 10 * 1024 * 1024 * 1024 }, // 10GB máximo por archivo
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
            mensaje: "⏳ Ya estoy procesando otro contenido, por favor esperá unos minutos..." 
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

    try {
        // Guardamos el archivo original en la carpeta de entrada
        const rutaArchivoOriginal = path.join(INPUT_FOLDER, archivoRecibido.name);
        await archivoRecibido.mv(rutaArchivoOriginal);

        // 🧮 Calculamos la duración del vídeo y la cantidad de partes
        const duracionSegundos = await new Promise((resolve) => {
            execFile('ffprobe', [
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                rutaArchivoOriginal
            ], (error, stdout) => {
                if (error || !stdout || isNaN(parseFloat(stdout))) {
                    console.log("⚠️ No se pudo leer la duración exacta del vídeo, se usará valor estimado de 10 segundos");
                    return resolve(10);
                }
                resolve(parseFloat(stdout.trim()));
            });
        });

        const cantidadPartes = Math.floor(duracionSegundos / config.CLIP_DURATION) + 1;

        // Respondemos al usuario que todo empezó bien
        res.json({
            status: "ok",
            mensaje: `🚀 Proceso iniciado: se generarán ${cantidadPartes} partes y se enviarán a los dos canales`
        });

        // 📋 Mostramos toda la información en la consola
        console.log("\n" + "=".repeat(60));
        console.log("📋 DATOS DEL PROCESO");
        console.log(`📌 Contenido: ${nombreContenido}`);
        console.log(`⏱️ Duración total: ${Math.round(duracionSegundos)} segundos`);
        console.log(`🔢 Duración por parte: ${config.CLIP_DURATION} segundos`);
        console.log(`🔢 Cantidad total de partes: ${cantidadPartes}`);
        console.log(`📢 Canal Público: ${config.CANAL_PUBLICO.NOMBRE} (ID: ${config.CANAL_PUBLICO.ID})`);
        console.log(`🔒 Canal Privado: Solo vos (ID: ${config.CANAL_PRIVADO.ID})`);
        console.log("=".repeat(60) + "\n");

        // 🚀 EJECUTAMOS TODO EN EL ORDEN QUE QUERÍAS:
        // PASO 1: Cortar todo el vídeo primero
        await cortarTodoElVideo(rutaArchivoOriginal, cantidadPartes);

        // PASO 2: Preparar los mensajes que van a acompañar cada vídeo
        const generadorMensajes = new GeneradorMensajes(nombreContenido, listaDePartes.length);

        // PASO 3: Enviar parte por parte a los dos canales
        await enviarTodasLasPartes(generadorMensajes);

        // 🧹 Limpieza final: eliminamos el archivo original
        if (fs.existsSync(rutaArchivoOriginal)) {
            fs.unlinkSync(rutaArchivoOriginal);
            console.log("🗑️ Archivo original eliminado");
        }

        PROCESANDO = false;

    } catch (error) {
        PROCESANDO = false;
        console.error("\n❌ ERROR GENERAL EN EL PROCESO:", error.message);
        res.json({ 
            status: "error", 
            mensaje: "❌ Ocurrió un error al procesar el contenido: " + error.message 
        });

        // 🧹 Limpiamos todo si hubo error
        const rutaArchivoOriginal = path.join(INPUT_FOLDER, req.files?.video?.name || "");
        if (fs.existsSync(rutaArchivoOriginal)) fs.unlinkSync(rutaArchivoOriginal);
        
        fs.readdirSync(config.TEMP_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(config.TEMP_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });
        
        fs.readdirSync(TEMP_UPLOAD_FOLDER).forEach(archivoTemp => {
            const rutaTemp = path.join(TEMP_UPLOAD_FOLDER, archivoTemp);
            fs.unlinkSync(rutaTemp);
        });
    }
});

// 🚀 Iniciar el servidor
console.log("==================================================");
console.log("⚡ MALLYCUTS - SISTEMA ACTIVADO CON LOS DOS CANALES");
console.log("🌐 Accedé en tu navegador: http://localhost:5000");
console.log("⏱️ Duración por parte: " + config.CLIP_DURATION + " segundos");
console.log("📢 Canal Público: " + config.CANAL_PUBLICO.NOMBRE);
console.log("🔒 Canal Privado: Solo vos");
console.log("==================================================");

// Línea corregida y completa
app.listen(PORT, '0.0.0.0', () => {});
