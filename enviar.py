import telebot
import time
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(path_archivo, mensaje):
    """Envío con reintentos agresivos"""
    for i in range(1, config.MAX_RETRIES + 1):
        try:
            with open(path_archivo, 'rb') as v:
                bot.send_video(
                    config.CHAT_ID, v, caption=mensaje,
                    parse_mode="HTML", timeout=config.TIMEOUT_SEND,
                    supports_streaming=True
                )
            return True
        except Exception:
            time.sleep(10 * i)
    return False
