// ==============================================
// 🚀 SERVIDOR - ENTRY POINT
// ==============================================

const app = require('./app');
const logger = require('./middlewares/logger/logger');
const database = require('./config/database');
const telegram = require('./config/telegram');

const PORT = process.env.PORT || 3000;

// ==============================================
// 🔥 INICIAR SERVICIOS
// ==============================================
async function iniciarServidor() {
  try {
    // 1. Conectar Base de Datos
    await database.conectar();
    
    // 2. Inicializar Bot de Telegram
    await telegram.inicializar();

    // 3. Encender Servidor HTTP
    app.listen(PORT, () => {
      logger.separador();
      logger.exito(`✅ SERVIDOR MALLYCUTS ACTIVO`);
      logger.info(`🌐 URL: http://localhost:${PORT}`);
      logger.info(`📂 Modo: ENTERPRISE EDITION`);
      logger.separador();
    });

  } catch (error) {
    logger.error('💥 ERROR AL INICIAR SISTEMA', error);
    process.exit(1);
  }
}

// ==============================================
// 🛡️ MANEJO DE EXCEPCIONES GLOBALES
// ==============================================
process.on('unhandledRejection', (reason) => {
  logger.error('⚠️ UNHANDLED REJECTION', reason);
});

process.on('uncaughtException', (error) => {
  logger.error('💥 UNCAUGHT EXCEPTION', error);
  process.exit(1);
});

// 🚀 GO!
iniciarServidor();
