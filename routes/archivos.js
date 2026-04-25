const express = require('express');
const router = express.Router();
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs').promises;
const path = require('path');

// Importar motor de edición
const { extraerYEditarSegmento } = require('../core/cortar');

// ==============================================
// 🚀 RUTA PRINCIPAL - MODO RÁPIDO Y SEGURO
// ==============================================
router.post('/procesar', async (req, res) => {
    
    log.separador();
    log.info('📥 NUEVA SOLICITUD DE PROCESAMIENTO');
    log.aviso('⚡ Modo: BACKGROUND PROCESSING');
    log.aviso('✅ Respuesta rápida | Servidor libre');

    // 1️⃣ EXTRAER Y VALIDAR DATOS
    const { titulo, archivo } = req.body;

    if (!titulo || !archivo) {
        log.error('❌ Faltan datos obligatorios');
        return res.status(400).json({ 
            status: 'error', 
            mensaje: 'Faltan datos (Título o Archivo)' 
        });
    }

    // 🔒 SEGURIDAD: Evitar path traversal (hackeos)
    if (archivo.includes('..') || archivo.includes('/') || archivo.includes('\\')) {
        log.error(`❌ Intento de ruta inválida: ${archivo}`);
        return res.status(400).json({ 
            status: 'error', 
            mensaje: 'Nombre de archivo no permitido' 
        });
    }

    // 2️⃣ CONSTRUIR RUTA
    const rutaCompleta = path.join(config.CARPETA_ENTRADA, archivo);

    // 3️⃣ VERIFICAR ARCHIVO (MODO ASÍNCRONO)
    try {
        await fs.access(rutaCompleta);
        log.dato(`📄 Archivo verificado: ${archivo}`);
    } catch {
        log.error(`❌ Archivo NO existe en disco: ${rutaCompleta}`);
        return res.status(404).json({ 
            status: 'error', 
            mensaje: 'El archivo no se encontró en el servidor' 
        });
    }

    // ==============================================
    // 🚀 LANZAR EN SEGUNDO PLANO
    // ==============================================
    
    log.inicio(`🔄 ENCOLADO: ${titulo}`);
    
    // 🔥 AQUÍ ESTÁ LA MAGIA: NO USAMOS AWAIT
    // El servidor responde YA y el proceso corre solo
    extraerYEditarSegmento(rutaCompleta, titulo)
        .then(() => {
            log.exito(`✅ COMPLETADO: ${titulo}`);
        })
        .catch((err) => {
            log.error(`💥 FALLÓ: ${titulo}`, err);
        });

    // RESPUESTA INMEDIATA AL USUARIO
    return res.json({
        status: 'ok',
        mensaje: `⏳ PROCESANDO EN SEGUNDO PLANO: ${titulo}`
    });

});

module.exports = router;
