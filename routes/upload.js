const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const config = require('../config');
const log = require('../js/logger');

// ==============================================
// 📂 CONFIGURACIÓN MULTER
// ==============================================
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, config.CARPETA_ENTRADA);
    },
    filename: function (req, file, cb) {
        // Obtener el título que viene del formulario
        const titulo = req.body.titulo || 'video';
        // Limpiar el nombre para que no tenga espacios raros
        const tituloLimpio = titulo.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]/g, '').trim();
        const nombreFinal = `${tituloLimpio}_${Date.now()}${path.extname(file.originalname)}`;
        cb(null, nombreFinal);
    }
});

const upload = multer({ 
    storage: storage,
    limits: { fileSize: 10 * 1024 * 1024 * 1024 } // 10GB
}).single('archivo_video');

// ==============================================
// 📤 RUTA DE SUBIDA
// ==============================================
router.post('/', (req, res) => {
    upload(req, res, function (err) {
        if (err) {
            log.error('Error al subir: ' + err.message);
            return res.json({ status: 'error', mensaje: err.message });
        }

        // ✅ AQUÍ ESTABA EL ERROR
        // Ahora sí enviamos los datos correctos al frontend
        res.json({ 
            status: 'ok', 
            archivo: req.file.filename,
            titulo: req.body.titulo
        });
        
        log.exito(`Archivo subido: ${req.file.filename} | Título: ${req.body.titulo}`);
    });
});

module.exports = router;
