const express = require('express');
const router = express.Router();
const log = require('../js/logger');

// 🔗 Ruta para descargar desde link
router.post('/procesar', async (req, res) => {
    try {
        const { url, titulo } = req.body;
        
        // Aquí iría el código de descarga
        log.info(`Solicitud: ${titulo} | ${url}`);

        res.json({ 
            status: 'ok', 
            mensaje: 'Link recibido y listo para descargar' 
        });

    } catch (error) {
        res.json({ status: 'error', mensaje: error.message });
    }
});

module.exports = router;
