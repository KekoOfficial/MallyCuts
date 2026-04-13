import os, subprocess, time
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)

def despachar_a_telegram(path_video, caption):
    path_thumb = path_video.replace(".mp4", ".jpg")
    
    # Miniatura balanceada
    subprocess.run(['ffmpeg', '-y', '-i', path_video, '-ss', '00:00:01', '-vframes', '1', path_thumb], capture_output=True)
    
    # Reintentos automáticos si falla la red
    for intento in range(3):
        try:
            with open(path_video, 'rb') as v, open(path_thumb, 'rb') as t:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, 
                               parse_mode="HTML", timeout=800, supports_streaming=True)
            break
        except Exception as e:
            print(f"⚠️ Intento {intento+1} fallido: {e}")
            time.sleep(10)
    
    # Limpieza estricta
    if os.path.exists(path_video): os.remove(path_video)
    if os.path.exists(path_thumb): os.remove(path_thumb)
