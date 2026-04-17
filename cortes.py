import telebot
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

def enviar_video(ruta, caption):
    """Envía el clip con soporte para streaming."""
    try:
        with open(ruta, 'rb') as v:
            bot.send_video(config.CHAT_ID, v, caption=caption, 
                           supports_streaming=True, timeout=300)
        return True
    except Exception as e:
        print(f"Error en envío: {e}")
        return False
