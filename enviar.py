import telebot, config, time

bot = telebot.TeleBot(config.BOT_TOKEN)

def subir_video(ruta, caption):
    for intento in range(config.MAX_RETRIES):
        try:
            with open(ruta, 'rb') as v:
                return bot.send_video(
                    config.CHAT_ID, v, 
                    caption=caption, 
                    supports_streaming=True, 
                    timeout=config.TIMEOUT_SEND
                )
        except Exception:
            if intento < config.MAX_RETRIES - 1:
                time.sleep(5) # Espera técnica antes de reintentar
            continue
    return False
