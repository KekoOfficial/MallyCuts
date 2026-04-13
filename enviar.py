import os
import subprocess
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)

def despachar_a_telegram(path_video, caption):
    """Genera thumb y envía. Limpia archivos al terminar."""
    path_thumb = path_video.replace(".mp4", ".jpg")
    
    # Miniatura del segundo 1
    subprocess.run(['ffmpeg', '-y', '-i', path_video, '-ss', '00:00:01', '-vframes', '1', path_thumb], capture_output=True)
    
    try:
        with open(path_video, 'rb') as v, open(path_thumb, 'rb') as t:
            bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML", timeout=600)
    finally:
        # Borrado inmediato para liberar espacio
        if os.path.exists(path_video): os.remove(path_video)
        if os.path.exists(path_thumb): os.remove(path_thumb)
