import logging
import os
from datetime import datetime

# Asegurar que la carpeta de logs exista
LOG_DIR = "data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Nombre del archivo basado en la fecha actual
log_filename = os.path.join(LOG_DIR, f"mally_{datetime.now().strftime('%Y-%m-%d')}.log")

def configurar_logger():
    """Configura el sistema de registro profesional."""
    logger = logging.getLogger("MallyCuts")
    logger.setLevel(logging.INFO)

    # Formato: Fecha - Nivel - Mensaje
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                                  datefmt='%H:%M:%S')

    # 1. Grabado en Archivo
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(formatter)

    # 2. Salida por Consola (opcional para seguir viendo en Termux)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Evitar duplicados si se llama varias veces
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

# Instancia global para usar en todo el proyecto
mally_log = configurar_logger()
