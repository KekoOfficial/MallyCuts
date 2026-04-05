# =====================================================
# 🎬 MALLY SERIES PRO - CONFIGURACIÓN MAESTRA
# =====================================================

# --- 🔑 CREDENCIALES DE TELEGRAM ---
# Obtén tu token en @BotFather
API_TOKEN = "TU_TOKEN_AQUÍ"

# ID del Canal o Grupo donde se enviarán los videos (ej: -100123456789)
CHAT_ID = "ID_DEL_CANAL_O_GRUPO"

# Tu ID personal de usuario para funciones administrativas
ADMIN_ID = "TU_ID_DE_USUARIO"


# --- ⚙️ PARÁMETROS DE PRODUCCIÓN ---
# Duración exacta de cada clip en segundos (60 = 1 minuto)
CLIP_DURATION = 60

# Carpeta base donde se guardarán temporalmente los episodios
TEMP_FOLDER = "producciones_mally"

# Puerto para la interfaz web de Termux
PORT = 5000


# --- 🛡️ ESCUDO ANTI-TIMEOUT (RED ROBUSTA) ---
# Tiempo máximo (segundos) esperando respuesta de subida (Recomendado: 600)
READ_TIMEOUT = 600

# Tiempo máximo (segundos) para establecer conexión inicial
CONNECT_TIMEOUT = 80

# Número de intentos si un episodio falla antes de pasar al siguiente
MAX_RETRIES = 3


# --- 💎 PERSONALIZACIÓN EXTRA ---
# Nombre de la marca que aparece en los mensajes
BRAND_NAME = "MALLY SERIES"

# User de Telegram para créditos en el caption
CHANNEL_USER = "@MallySeries"
