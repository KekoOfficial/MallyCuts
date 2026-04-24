const express = require('express');
const router = express.Router();
const log = require('../js/logger');
const { extraerYEditarSegmento } = require('../core/cortar');

// ✂️ Ruta para cortar
router.post('/iniciar', async (req, res) => {
    try {
        const { rutaArchivo, numeroParte, titulo } = req.body;
        const resultado = await extraerYEditarSegmento(rutaArchivo, numeroParte, titulo);
        res.json({ status: 'ok', ruta: resultado });
    } catch (error) {
        res.json({ status: 'error', mensaje: error.message });
    }
});

module.exports = router;
