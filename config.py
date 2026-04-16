import os

# --- MALLY SERIES CONFIG ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# Producción y Rutas
TEMP_FOLDER = "mally_studio_segments"
CLIP_DURATION = 60  

# Branding Central Premium
WATERMARK_TEXT = "t.me/MallySeries"
WATERMARK_COLOR = "white@0.5" 
WATERMARK_SIZE = 32

# Configuración de Red e Inteligencia
MAX_RETRIES = 5        # Aumentado para mayor estabilidad
TIMEOUT_SEND = 300     # 5 minutos para asegurar subidas pesadas
MAX_CONCURRENT_JOBS = 2 # Evita que el móvil se caliente
PAUSA_ENTRE_CAPS = 2   # Respiro para la API de Telegram

# Calidad de Video (Optimizado para TikTok @escenaen15)
VIDEO_CODEC = "libx264"
CRF_VALUE = "23"       # Balance perfecto entre peso y calidad
PRESET = "ultrafast"   # Velocidad máxima de procesado
