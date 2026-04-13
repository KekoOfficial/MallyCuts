import telebot
import config
import time
import os

bot = telebot.TeleBot(config.BOT_TOKEN)

def despachar_a_telegram(path_archivo, mensaje):
    """
    Envía el video a Telegram con sistema de reintentos.
    """
    max_intentos = 3
    for intento in range(1, max_intentos + 1):
        try:
            with open(path_archivo, 'rb') as video:
                bot.send_video(
                    config.CHAT_ID, 
                    video, 
                    caption=mensaje, 
                    parse_mode="HTML",
                    timeout=120 # Aumentamos tiempo de espera para archivos grandes
                )
            return True # Éxito total
            
        except Exception as e:
            print(f"⚠️ Intento {intento} fallido para {path_archivo}: {e}")
            if "Too Large" in str(e):
                print("🛑 Archivo excede límites de Telegram. Saltando...")
                return False
            
            if intento < max_intentos:
                time.sleep(10) # Espera 10 segundos antes de reintentar
            else:
                print(f"❌ Imposible enviar {path_archivo} tras {max_intentos} intentos.")
                return False
