import os

# ──── CREDENCIALES TELEGRAM ────
TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# ──── RUTAS DEL SISTEMA ────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "videos")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
LOGS_FOLDER = os.path.join(BASE_DIR, "data", "logs")

# ──── PARÁMETROS DE CALIDAD ────
RESOLUCION = "1920:1080"      # Full HD
CODEC_VIDEO = "libx264"
CODEC_AUDIO = "aac"
BITRATE_AUDIO = "128k"
CRF_QUALITY = "23"            # 18-28 = Rango Calidad
PRESET = "medium"              # fast / medium / slow

# ──── SEGURIDAD Y RENDIMIENTO ────
DURACION_POR_PARTE = 60       # Segundos
TIMEOUT_FFMPEG = 900          # Segundos max por corte
TIMEOUT_TELEGRAM = 300        # Segundos max subida
REINTENTOS_ENVIO = 3           # Veces que intenta si falla
PAUSA_ENTRE_ENVIOS = 2        # Segundos entre video y video

# ──── CREAR CARPETAS SI NO EXISTEN ────
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)
