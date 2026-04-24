const express = require('express');
const router = express.Router();
const config = require('../config');
const log = require('../js/logger');

// ⚙️ Ver configuración actual
router.get('/', (req, res) => {
    res.json({
        sistema: 'MallyCuts',
        version: '2.0',
        velocidad: config.VELOCIDAD_VIDEO,
        duracion: config.DURACION_POR_PARTE,
        marca: config.TEXTO_MARCA_AGUA
    });
});

module.exports = router;
