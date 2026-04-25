const express = require('express');
const router = express.Router();
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs');
const path = require('path');

// ==============================================
// 🚀 RUTA PRINCIPAL DE PROCESO
// ==============================================
router.post('/procesar', async (req, res) => {
    
    log.separador();
    log.info('📥 NUEVA SOLICITUD DE PROCESAMIENTO');
    log.aviso('⚠️  Modo: CORTE RÁPIDO + EDICIÓN POR PARTES');
    log.aviso('⚠️  Los resultados saldrán mucho más rápido!');

    // ==============================================
    // ✅ AQUÍ ESTA LA SOLUCIÓN
    // ==============================================
    
    // MOSTRAR EN CONSOLA LO QUE LLEGA (PARA VER EL ERROR)
    console.log("👉 DATOS RECIBIDOS:", req.body);

    const titulo = req.body.titulo;
    const archivo = req.body.archivo;

    // VERIFICAR SI LLEGARON
    if(!titulo || !archivo) {
        log.error(`❌ FALTAN DATOS -> Titulo: ${titulo}, Archivo: ${archivo}`);
        return res.json({ 
            status: 'error', 
            mensaje: 'Faltan datos obligatorios' 
        });
    }

    // ==============================================
    // ✅ SI LLEGARON BIEN, CONTINUAR
    // ==============================================

    log.exito(`✅ DATOS RECIBIDOS CORRECTAMENTE:`);
    log.dato(`📝 Título: ${titulo}`);
    log.dato(`📄 Archivo: ${archivo}`);

    const rutaCompleta = path.join(config.CARPETA_ENTRADA, archivo);

    // Verificar si el archivo existe físicamente
    if(!fs.existsSync(rutaCompleta)) {
        log.error(`❌ El archivo NO existe en: ${rutaCompleta}`);
        return res.json({ status: 'error', mensaje: 'Archivo no encontrado en disco' });
    }

    // ==============================================
    // 🎬 AQUÍ IRÍA EL CÓDIGO DE FFMPEG / CORTE
    // ==============================================
    log.inicio('🔄 Iniciando motor de edición...');
    
    // Aquí conectarías con tu función de cortar videos
    // await cortarVideo(rutaCompleta, titulo);

    res.json({ 
        status: 'ok', 
        mensaje: `✅ Proceso iniciado para: ${titulo}` 
    });

    log.separador();
});

module.exports = router;
