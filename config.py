import os

# ⚔️ CREDECIALES TELEGRAM
TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"

# 📂 RUTAS DEL SISTEMA
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "videos")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")
LOGS_FOLDER = os.path.join(BASE_DIR, "data", "logs")

# ==============================================
# ⚡⚡⚡ CONFIGURACIÓN DE VELOCIDAD EXTREMA ⚡⚡⚡
# ==============================================
# Para que corte y procese lo más rápido posible
# sin consumir tanta memoria

PRESET = "ultrafast"      # 🚀 MÁS RÁPIDO POSIBLE (antes veryfast)
CRF_QUALITY = "27"        # ⚖️ Compresión ideal: Rápido + Calidad decente
THREADS = "4"             # 🧠 Usa todos los núcleos disponibles

# 🎬 FORMATO Y RESOLUCIÓN
RESOLUCION = "1080:1920" # 📱 MODO VERTICAL FORZADO
DURACION_POR_PARTE = 50  # ⏱️ Partes de 50 seg (termina más rápido cada corte)

# 🎥 CODECS Y CALIDAD
CODEC_VIDEO = "libx264"
CODEC_AUDIO = "aac"
BITRATE_AUDIO = "128k"
PIXEL_FORMAT = "yuv420p" # Compatibilidad total

# ⏱️ TIEMPOS Y SEGURIDAD
TIMEOUT_FFMPEG = 900      # ⏳ 15 minutos máximo por parte (para videos largos)
TIMEOUT_TELEGRAM = 300    # ⏳ 5 minutos para subir
REINTENTOS_ENVIO = 3
PAUSA_ENTRE_ENVIOS = 3    # Pequeña pausa para no saturar

# 📂 CREAR CARPETAS AUTOMÁTICAMENTE
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
os.makedirs(LOGS_FOLDER, exist_ok=True)

# ==============================================
# ✅ ESTADO DEL SISTEMA
# ==============================================
print("="*50)
print("⚔️ MALLYCUTS - CONFIGURACIÓN CARGADA ⚔️")
print(f"⚡ Modo Velocidad: {PRESET.upper()}")
print(f"📏 Resolución: {RESOLUCION}")
print(f"⏱️ Duración por parte: {DURACION_POR_PARTE}s")
print("="*50)
