import os

# ==========================================
#   UMBRAE STUDIO - CORE INFRASTRUCTURE
# ==========================================

# Identidad del Bot y Destino
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# Canales de Distribución Oficial
TG_OFFICIAL = "t.me/MallySeries"
TT_OFFICIAL = "@EscenaDe15"
STUDIO_NAME = "Umbrae Studio"

# ==========================================
#   PARÁMETROS DE PRODUCCIÓN (MALLY SERIES)
# ==========================================

# Gestión de Archivos
TEMP_FOLDER = "mally_studio_segments"
CLIP_DURATION = 60  # Segundos exactos por capítulo

# Renderizado de Video (Optimización Escena de 15)
VIDEO_CODEC = "libx264"
PRESET_SPEED = "ultrafast"  # Velocidad máxima para Termux
CRF_QUALITY = "23"          # Balance peso/nitidez premium
VIDEO_BITRATE = "2500k"     # Bitrate estable para subida rápida
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "128k"

# ==========================================
#   ESTÉTICA & BRANDING (UMBRAE STYLE)
# ==========================================

# Marca de Agua Inteligente
WATERMARK_TEXT = f"TG: MallySeries | TT: EscenaDe15"
WATERMARK_COLOR = "white@0.4" # Look translúcido profesional
WATERMARK_SIZE = 28           # Tamaño balanceado para móvil
SHADOW_OPACITY = 0.6          # Sombra para lectura en escenas claras

# ==========================================
#   INTELIGENCIA DE RED Y RECURSOS
# ==========================================

# Sincronización y Estabilidad
MAX_RETRIES = 7               # Aumentado para zonas de baja señal
TIMEOUT_SEND = 600            # 10 min de espera para archivos pesados
PAUSA_ENTRE_CAPS = 3          # Evita el FloodWait de Telegram
MAX_CONCURRENT_JOBS = 2       # Protección térmica para el procesador

# Logging y Debug
LOG_FILE = "umbras_studio_core.log"
DEBUG_MODE = False            # Cambiar a True para ver errores de FFmpeg
