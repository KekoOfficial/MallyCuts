import os

# ==========================================
#   UMBRAE STUDIO - CONFIGURACIÓN CORE
#   (Identidad & Privacidad Blindada)
# ==========================================

# Identidad del Bot y Destino Oficial (Mally Series)
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
# Canal/Grupo Mally Series (donde van las series completas)
CHAT_ID_CANAL = "-1003584710096" 

# --- PRIVACIDAD MAESTRA: TU ID PERSONAL ---
# Pon aquí tu ID personal de Telegram (ej: "8630490789")
# Para que el Bot te notifique solo a ti en privado.
ADMIN_PERSONAL_ID = "8630490789" 

# Branding Oficial & Distribución
TG_OFFICIAL = "t.me/MallySeries"
TT_OFFICIAL = "@EscenaDe15"
STUDIO_NAME = "Umbrae Studio"

# ==========================================
#   PARÁMETROS DE PRODUCCIÓN LOCAL (Termux)
# ==========================================

# Gestión de Archivos (Rutas en Termux)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Carpeta de producción unificada
PRODUCTION_FOLDER = os.path.join(BASE_DIR, "mally_studio_production") 
os.makedirs(PRODUCTION_FOLDER, exist_ok=True)

# Lógica de Cortes Automáticos (antiguo cortes.py)
# El sistema dividirá el video original en esta cantidad de partes iguales (ej: 2)
NUM_SEGMENTS_AUTOCUT = 2 

# Renderizado de Video (Optimización FFmpeg para móvil)
VIDEO_CODEC = "libx264"
PRESET_SPEED = "ultrafast"  # Velocidad máxima para el CPU de Termux
CRF_QUALITY = "23"          # Balance premium peso/nitidez
VIDEO_BITRATE = "2500k"     # Bitrate estable para subida local
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"

# Estética & Marca de Agua (lógica marcas.py)
WATERMARK_TEXT = f"TG: MallySeries | TT: EscenaDe15"
WATERMARK_COLOR = "white@0.4" # Look translúcido profesional
WATERMARK_SIZE = 28           # Tamaño balanceado para móvil
SHADOW_OPACITY = 0.6          # Sombra para lectura en escenas claras

# Inteligencia de Red y Recursos Local
MAX_RETRIES = 7               # Aumentado para zonas de baja señal
TIMEOUT_SEND = 600            # 10 min de espera para archivos pesados
PAUSA_ENTRE_CAPS = 3          # Evita FloodWait de Telegram (lógica cortes.py)
MAX_CONCURRENT_JOBS = 1       # Protección térmica ESTRICTA para Termux
MAX_UPLOAD_SIZE_MB = 1024     # Límite de subida (1GB) para Web Local (Puerto 8000)

# Logging y Debug (lógica logger.py)
LOG_FILE = os.path.join(BASE_DIR, "umbras_studio_core.log")
DEBUG_MODE = False            # Cambiar a True para ver errores de FFmpeg
