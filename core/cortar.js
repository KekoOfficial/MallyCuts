const express = require('express');
const router = express.Router();
const log = require('../js/logger');
const config = require('../config');
const fs = require('fs');
const path = require('path');

// ✅ IMPORTAR LA FUNCIÓN DE CORTAR
const { extraerYEditarSegmento } = require('../core/cortar');

// ==============================================
// 🚀 RUTA PRINCIPAL DE PROCESO
// ==============================================
router.post('/procesar', async (req, res) => {
    
    log.separador();
    log.info('📥 NUEVA SOLICITUD DE PROCESAMIENTO');
    log.aviso('⚠️  Modo: CORTE RÁPIDO + EDICIÓN POR PARTES');
    log.aviso('⚠️  Los resultados saldrán mucho más rápido!');

    const titulo = req.body.titulo;
    const archivo = req.body.archivo;

    if(!titulo || !archivo) {
        log.error(`❌ FALTAN DATOS -> Titulo: ${titulo}, Archivo: ${archivo}`);
        return res.json({ status: 'error', mensaje: 'Faltan datos obligatorios' });
    }

    log.exito(`✅ DATOS RECIBIDOS CORRECTAMENTE:`);
    log.dato(`📝 Título: ${titulo}`);
    log.dato(`📄 Archivo: ${archivo}`);

    const rutaCompleta = path.join(config.CARPETA_ENTRADA, archivo);

    if(!fs.existsSync(rutaCompleta)) {
        log.error(`❌ El archivo NO existe en: ${rutaCompleta}`);
        return res.json({ status: 'error', mensaje: 'Archivo no encontrado en disco' });
    }

    // ==============================================
    // 🎬 INICIAR CORTE REAL
    // ==============================================
    try {
        log.inicio('🔄 Iniciando motor FFMPEG...');
        
        // 🚀 ESTO LLAMA A TU CÓDIGO QUE HACE EL MILAGRO
        await extraerYEditarSegmento(rutaCompleta, titulo);

        log.exito('✅ PROCESO FINALIZADO COMPLETO');
        res.json({ status: 'ok', mensaje: '✅ Video cortado y listo!' });

    } catch (error) {
        log.error('💥 ERROR EN EL CORTE:', error);
        res.json({ status: 'error', mensaje: 'Error: ' + error.message });
    }

    log.separador();
});

module.exports = router;
