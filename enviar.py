import telebot
import config
import time

bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(video_path, caption):
    for intento in range(config.MAX_RETRIES):
        try:
            with open(video_path, 'rb') as video:
                bot.send_video(
                    config.CHAT_ID, 
                    video, 
                    caption=caption, 
                    parse_mode="HTML",
                    timeout=config.TIMEOUT_SEND
                )
            return True
        except Exception as e:
            print(f"⚠️ Intento {intento+1} fallido: {e}")
            time.sleep(10) # Espera antes de reintentar
    return False
