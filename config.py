# --- Configuración de Telegram ---
API_TOKEN = "TU_TOKEN_DE_TELEGRAM"
CHAT_ID = "EL_ID_DE_TU_CANAL_O_GRUPO"
ADMIN_ID = "TU_ID_DE_USUARIO"

# --- Parámetros de Hyper-Velocidad ---
CLIP_DURATION = 60  # Segundos por clip
TEMP_FOLDER = "mally_studio_segments"
PORT = 5000

# --- Ajustes de Red (Anti-Timeout) ---
# Tiempo máximo de espera para la subida (10 minutos por archivo)
READ_TIMEOUT = 600
CONNECT_TIMEOUT = 60
# Intentos por cada episodio si falla la subida
MAX_RETRIES = 3
