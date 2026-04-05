import os

# --- CREDENCIALES ---
API_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096" 

# --- DESCARGA (yt-dlp) ---
THREADS = 8
YTDL_OPTS = {
    'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'concurrent_fragments': THREADS,
    'noprogress': True,
    'quiet': True,
}

# --- PROCESAMIENTO ---
CLIP_DURATION = 300  # 5 minutos por clip
TEMP_FOLDER = "mally_workdir"
PORT = 5000

# --- RED Y TIEMPOS ---
READ_TIMEOUT = 600
CONNECT_TIMEOUT = 60
MAX_RETRIES = 3
SLEEP_BETWEEN_POSTS = 4

if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
