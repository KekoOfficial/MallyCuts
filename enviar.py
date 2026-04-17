import telebot, config

bot = telebot.TeleBot(config.BOT_TOKEN)

def subir_video(ruta, caption):
    """Sube el video al canal con margen de tiempo extendido."""
    with open(ruta, 'rb') as v:
        return bot.send_video(
            config.CHAT_ID, v, 
            caption=caption, 
            supports_streaming=True, 
            timeout=180
        )
