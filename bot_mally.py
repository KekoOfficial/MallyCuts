import telebot
from telebot import apihelper
import config

apihelper.READ_TIMEOUT = config.READ_TIMEOUT
apihelper.CONNECT_TIMEOUT = config.CONNECT_TIMEOUT
bot = telebot.TeleBot(config.API_TOKEN)

def enviar_clip(video_path, thumb_path, caption):
    with open(video_path, 'rb') as v:
        with open(thumb_path, 'rb') as t:
            return bot.send_video(
                config.CHAT_ID, v, thumb=t, 
                caption=caption, parse_mode="HTML", 
                timeout=config.READ_TIMEOUT
            )

def enviar_texto(texto):
    return bot.send_message(config.CHAT_ID, texto, parse_mode="HTML")
