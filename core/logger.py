import logging
import os
from datetime import datetime
from config import LOGS_FOLDER

def setup_logger():
    logger = logging.getLogger("MallyCuts")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%d/%m %H:%M:%S'
    )
    
    # Archivo de log diario
    log_file = os.path.join(LOGS_FOLDER, f"actividad_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Evitar duplicados
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

log = setup_logger()
