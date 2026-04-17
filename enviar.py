import telebot

BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"
bot = telebot.TeleBot(BOT_TOKEN)

def enviar_video(ruta_file, caption):
    """Envía el clip procesado al canal."""
    try:
        with open(ruta_file, 'rb') as v:
            bot.send_video(CHAT_ID, v, caption=caption, supports_streaming=True, timeout=300)
        return True
    except Exception as e:
        print(f"Error envío: {e}")
        return False
