import time
import os
import sys
# Importa la infraestructura unificada
try:
    import config as cfg
except ImportError:
    print("❌ Errorlogger: No se encontró config.py.")
    sys.exit(1)

def registrar_log(mensaje):
    """Función de logging centralizada en config.LOG_FILE"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] 👑 {cfg.STUDIO_NAME} {mensaje}\n"
    # Imprimir en consola de Termux
    print(log_entry.strip())
    # Guardar en archivo
    with open(cfg.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)
