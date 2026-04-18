import telebot
import time
import os
import config

bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(path_archivo, mensaje):
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
            print("✅ Enviado con éxito")
            return True
            
        except Exception as e:
            err = str(e)
            if "413" in err or "Too Large" in err:
                print(f"🛑 Muy pesado, saltando...")
                return False
            
            print(f"⚠️ Intento {intento} fallido: {err}")
            if intento < config.MAX_RETRIES:
                time.sleep(10 * intento)
            else:
                return False
