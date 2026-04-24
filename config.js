// ==============================================
// ⚙️ ARCHIVO DE CONFIGURACIÓN - MALLYCUTS
// ==============================================
// Sistema automatizado de procesamiento y envío
// Configuración completa y organizada
// ==============================================

const fs = require('fs');
const path = require('path');

// ==============================================
// 🤖 CONFIGURACIÓN DEL BOT Y CANALES
// ==============================================

const CONFIGURACION_TELEGRAM = {
    // 🗝️ Token de acceso al Bot
    TOKEN: "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI",

    // 📢 Canal Público (Marca / Audiencia)
    CANAL_PUBLICO: {
        ID: "-1003983527231",
        NOMBRE: "EnseñaEn15"
    },

    // 🔒 Canal Privado (Almacenamiento / Respaldo)
    CANAL_PRIVADO: {
        ID: "-1003706372741"
    }
};

// ==============================================
// ⚙️ PARÁMETROS DE FUNCIONAMIENTO
// ==============================================

const PARAMETROS_SISTEMA = {
    // Duración de cada fragmento en segundos
    DURACION_POR_PARTE: 60,
    
    // Control de errores y tiempos
    INTENTOS_MAXIMOS: 3,
    TIEMPO_ESPERA_ENVIO: 300000, // 5 minutos
    TAMANIO_MAXIMO_POR_ARCHIVO: 50 * 1024 * 1024, // Límite API Telegram: 50MB

    // Ajustes de edición de video
    VELOCIDAD_VIDEO: 1.3,
    TEXTO_MARCA_AGUA: "EnseñaEn15",

    // Limpieza automática
    ELIMINAR_ARCHIVOS_AL_TERMINAR: true
};

// ==============================================
// 📂 RUTAS DE CARPETAS DE TRABAJO
// ==============================================

const RUTAS_CARPETAS = {
    CARPETA_TEMPORAL:     path.join(__dirname, 'videos', 'output'),
    CARPETA_ORIGINALES:   path.join(__dirname, 'videos', 'originales'),
    CARPETA_ENTRADA:      path.join(__dirname, 'videos', 'input'),
    CARPETA_SUBIDAS_TEMP: path.join(__dirname, 'temp_uploads')
};

// ==============================================
// 📦 EXPORTAMOS TODO PARA USAR EN EL SISTEMA
// ==============================================

module.exports = {
    // Unificamos todo en un solo objeto para facilitar la importación
    ...CONFIGURACION_TELEGRAM,
    ...PARAMETROS_SISTEMA,
    ...RUTAS_CARPETAS
};

// ==============================================
// 🛠️ CREACIÓN AUTOMÁTICA DE ESTRUCTURA
// ==============================================

const TODAS_LAS_RUTAS = Object.values(RUTAS_CARPETAS);

TODAS_LAS_RUTAS.forEach(ruta => {
    try {
        if (!fs.existsSync(ruta)) {
            fs.mkdirSync(ruta, { recursive: true, mode: 0o777 });
            console.log(`📂 [CONFIG] Carpeta creada: ${ruta}`);
        } else {
            console.log(`✅ [CONFIG] Carpeta lista: ${ruta}`);
        }
    } catch (error) {
        console.error(`❌ [CONFIG] Error en: ${ruta}`, error.message);
    }
});

// ==============================================
// ✅ CONFIGURACIÓN CARGADA CORRECTAMENTE
// ==============================================
console.log("🚀 Configuración de MallyCuts cargada y lista para funcionar");
