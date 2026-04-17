import os

# 🔐 Seguridad: Busca en el sistema, si no lo halla, usa tus IDs
TOKEN = os.getenv("BOT_TOKEN", "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU")
CHAT_ID = os.getenv("CHAT_ID", "-1003584710096")

# 📁 Carpetas
UPLOAD_FOLDER = "videos"
PORTADA_FOLDER = "static"
FOTO_PORTADA = os.path.join(PORTADA_FOLDER, "temp_portada.jpg")

# ⚡ Config extra (Potencia MallyCuts)
MAX_WORKERS = 4          # Cortes en paralelo
TIMEOUT_TELEGRAM = 300   # Tiempo límite de subida
REINTENTOS = 3           # Reintentos si falla la red
