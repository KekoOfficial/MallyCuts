const express = require('express');
const router = express.Router();
const log = require('../js/logger');
const { enviarADosCanales } = require('../core/enviar');

// 📤 Ruta para probar envío
router.post('/enviar', async (req, res) => {
    try {
        const { ruta, mensaje } = req.body;
        await enviarADosCanales(ruta, mensaje, 1);
        res.json({ status: 'ok', mensaje: 'Enviado a Telegram' });
    } catch (error) {
        res.json({ status: 'error', mensaje: error.message });
    }
});

module.exports = router;
