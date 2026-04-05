import telebot
from telebot import apihelper
import config

apihelper.READ_TIMEOUT = config.READ_TIMEOUT
apihelper.CONNECT_TIMEOUT = config.CONNECT_TIMEOUT
bot = telebot.TeleBot(config.API_TOKEN)

def enviar_clip(v_path, t_path, cap):
    with open(v_path, 'rb') as v, open(t_path, 'rb') as t:
        return bot.send_video(config.CHAT_ID, v, thumb=t, caption=cap, parse_mode="HTML")

def enviar_msg(txt):
    return bot.send_message(config.CHAT_ID, txt, parse_mode="HTML")
