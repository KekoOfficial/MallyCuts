// ==============================================
// 🚀 SERVIDOR PRINCIPAL - MALLYCUTS
// ==============================================
// Configuración optimizada para archivos pesados
// ==============================================

const express = require('express');
const app = express();
const path = require('path');

// ==============================================
// ⚙️ CONFIGURACIÓN DE LÍMITES
// ==============================================

// 💡 LÍMITE ELIMINADO: Aceptar archivos de hasta 10GB
app.use(express.json({ limit: '10000mb' }));
app.use(express.urlencoded({ limit: '10000mb', extended: true }));

// Servir archivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// ==============================================
// 🧩 CARGA DE RUTAS
// ==============================================

const rutasProcesar = require('./routes/archivos');
app.use('/', rutasProcesar);

// ==============================================
// 🚀 INICIO DEL SERVIDOR
// ==============================================

const PUERTO = 3000;

app.listen(PUERTO, () => {
    console.log(`
======================================================================
                  ✅ SERVIDOR INICIADO CORRECTAMENTE
======================================================================
ℹ️ Dirección de acceso: http://localhost:${PUERTO}
ℹ️ Límite máximo de archivos: 10 GB
ℹ️ Estado: Listo para recibir archivos pesados
======================================================================
    `);
});
