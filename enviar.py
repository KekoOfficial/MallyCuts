import telebot
import config
import time
import os

# Usamos BOT_TOKEN que ya está definido en tu config
bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(path_archivo, mensaje):
    """Envío con reintentos y soporte de streaming"""
    for intento in range(1, config.MAX_RETRIES + 1):
        try:
            if not os.path.exists(path_archivo):
                print(f"❌ Error: {path_archivo} no encontrado.")
                return False

            with open(path_archivo, 'rb') as video:
                bot.send_video(
                    config.CHAT_ID, 
                    video, 
                    caption=mensaje, 
                    parse_mode="HTML",
                    timeout=config.TIMEOUT_SEND,
                    supports_streaming=True
                )
            return True
            
        except Exception as e:
            err = str(e)
            if "413" in err or "Too Large" in err:
                print(f"🛑 CAPÍTULO PESADO: {path_archivo} excede el límite. Saltando...")
                return False
            
            print(f"⚠️ Intento {intento} fallido: {err}")
            if intento < config.MAX_RETRIES:
                time.sleep(10 * intento)
            else:
                return False

def enviar_mensaje_final(texto):
    try:
        bot.send_message(config.CHAT_ID, texto, parse_mode="HTML")
    except:
        pass
