import telebot
import config
import time

bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(video_path, caption):
    """Envío con reintentos para soportar VPN lenta"""
    intentos = 3
    for i in range(intentos):
        try:
            with open(video_path, 'rb') as v:
                bot.send_video(
                    config.CHAT_ID, 
                    v, 
                    caption=caption, 
                    parse_mode="HTML", 
                    timeout=config.TIMEOUT_TELEGRAM
                )
            return True
        except Exception as e:
            print(f"⚠️ Reintento {i+1} en Telegram: {e}")
            time.sleep(5)
    return False
