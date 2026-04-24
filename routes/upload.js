const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const config = require('../config');
const log = require('../js/logger');

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, config.CARPETA_ENTRADA);
    },
    filename: function (req, file, cb) {
        const titulo = req.body.titulo || 'video';
        const nombreFinal = `${titulo}_${Date.now()}${path.extname(file.originalname)}`;
        cb(null, nombreFinal);
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 * 1024 }
}).single('archivo_video');

router.post('/', (req, res) => {
    upload(req, res, function (err) {
        if (err) {
            return res.json({ status: 'error', mensaje: err.message });
        }
        res.json({ 
            status: 'ok', 
            archivo: req.file.filename,
            titulo: req.body.titulo
        });
    });
});

module.exports = router;
