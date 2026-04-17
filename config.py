import os

# IDs de acceso
TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "videos")
PORTADA_FOLDER = os.path.join(BASE_DIR, "static")

# ⚡ POTENCIA CONTROLADA (Nivel Pro)
MAX_WORKERS = 2           # Reducido a 2 para estabilidad en videos largos
REINTENTOS_ENVIO = 3
TIMEOUT_FFMPEG = 600      # 10 min máximo por corte
CRF_QUALITY = "28"        # Balance peso/calidad
