import os

# --- MALLY SERIES CONFIG ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# Producción Express
TEMP_FOLDER = "mally_studio_segments"
CLIP_DURATION = 60  # Segundos por capítulo

# Branding Unificado
WATERMARK_TEXT = "t.me/MallySeries"
WATERMARK_COLOR = "white@0.5"
WATERMARK_SIZE = 32

# Inteligencia de Red
MAX_RETRIES = 3
TIMEOUT_SEND = 300 # 5 min por video

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
