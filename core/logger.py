import logging
import os
from datetime import datetime
from config import LOGS_FOLDER

# 🎨 COLORES PARA LA CONSOLA (ANSI)
class Colores:
    AMARILLO = '\033[93m'
    VERDE = '\033[92m'
    ROJO = '\033[91m'
    AZUL = '\033[94m'
    MORADO = '\033[95m'
    RESET = '\033[0m'
    NEGRITA = '\033[1m'

# Formateador personalizado con colores y emojis
class FormatoAvanzado(logging.Formatter):
    def format(self, record):
        # Emojis según el tipo de mensaje
        emojis = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'DEBUG': '🔍'
        }
        emoji = emojis.get(record.levelname, '•')
        
        # Aplicar colores
        if record.levelno == logging.ERROR:
            color = Colores.ROJO
        elif record.levelno == logging.WARNING:
            color = Colores.AMARILLO
        elif record.levelno == logging.INFO:
            color = Colores.VERDE
        else:
            color = Colores.AZUL

        # Formato final para consola
        formato_consola = (
            f"{Colores.NEGRITA}%(asctime)s{Colores.RESET} | "
            f"{color}{emoji} %(message)s{Colores.RESET}"
        )
        
        # Creamos un formateador temporal con este estilo
        temp_formatter = logging.Formatter(formato_consola, datefmt='%d/%m %H:%M:%S')
        return temp_formatter.format(record)

def setup_logger():
    logger = logging.getLogger("MallyCuts")
    logger.setLevel(logging.INFO)

    # 🧹 Limpiar handlers anteriores para no duplicar
    if logger.hasHandlers():
        logger.handlers.clear()

    # ==============================================
    # 📝 HANDLER 1: PARA ARCHIVO DE TEXTO (LOGS)
    # ==============================================
    # Guardamos todo en archivo con formato limpio (sin colores)
    log_file = os.path.join(LOGS_FOLDER, f"actividad_{datetime.now().strftime('%Y%m%d')}.log")
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%d/%m %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # ==============================================
    # 🖥️ HANDLER 2: PARA CONSOLA (CON COLORES)
    # ==============================================
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FormatoAvanzado())
    console_handler.setLevel(logging.INFO)

    # ==============================================
    # 🚀 ACTIVAR LOGGERS
    # ==============================================
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# 🎯 INSTANCIA GLOBAL PARA TODO EL SISTEMA
log = setup_logger()

# ✅ MENSAJE DE BIENVENIDA
log.info("="*60)
log.info("⚔️  SISTEMA MALLYCUTS - LOGS AVANZADOS ACTIVADOS  ⚔️")
log.info(f"📂 Guardando historial en: {LOGS_FOLDER}")
log.info("="*60)
