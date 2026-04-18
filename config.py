import os

# ⚔️ CREDECIALES TELEGRAM
TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# 📂 RUTAS DEL SISTEMA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "videos")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
LOGS_FOLDER = os.path.join(BASE_DIR, "data", "logs")

# ⚡⚡⚡ CONFIGURACIÓN DE VELOCIDAD MÁXIMA ⚡⚡⚡
PRESET = "veryfast"      # MODO RÁPIDO EXTREMO (antes era slow)
CRF_QUALITY = "26"       # Calidad buena pero archivo ligero y rápido
THREADS = "4"            # Usa todos los núcleos del procesador

# 🎬 FORMATO DE SALIDA
RESOLUCION = "1080:1920" # MODO VERTICAL FORZADO
DURACION_POR_PARTE = 60  # 1 minuto cada parte

# 🔊 AUDIO
CODEC_VIDEO = "libx264"
CODEC_AUDIO = "aac"
BITRATE_AUDIO = "128k"

# ⏱️ TIEMPOS DE ESPERA
TIMEOUT_FFMPEG = 600     # 10 minutos máximo por corte
TIMEOUT_TELEGRAM = 300   # 5 minutos para subir
REINTENTOS_ENVIO = 3
PAUSA_ENTRE_ENVIOS = 2

# 📂 CREAR CARPETAS AUTOMÁTICAMENTE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)
