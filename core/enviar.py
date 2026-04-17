import requests
import os
import time
import config
from core.logger import mally_log

# Sesión persistente para mayor velocidad en las 134 partes
session = requests.Session()

def subir_a_telegram(ruta, caption):
    """
    Envía el video a Telegram y confirma el éxito.
    Implementa reintentos en caso de lag de red.
    """
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
    
    if not os.path.exists(ruta):
        mally_log.error(f"⚠️ El archivo a enviar no existe: {ruta}")
        return False

    intentos = 0
    max_intentos = config.REINTENTOS_ENVIO # Definido en 3 en tu config

    while intentos < max_intentos:
        try:
            with open(ruta, "rb") as video_file:
                payload = {
                    "chat_id": config.CHAT_ID,
                    "caption": caption,
                    "supports_streaming": "true"
                }
                
                # Realizar la petición
                response = session.post(
                    url, 
                    data=payload, 
                    files={"video": video_file}, 
                    timeout=config.TIMEOUT_TELEGRAM
                )

            if response.status_code == 200:
                # Borrar archivo local inmediatamente después del éxito
                if os.path.exists(ruta):
                    os.remove(ruta)
                return True
            
            elif response.status_code == 429:
                # Si Telegram nos limita por flood (demasiados mensajes)
                espera = 15 # Esperamos 15 segundos
                mally_log.warning(f"⚠️ Flood limit. Esperando {espera}s...")
                time.sleep(espera)
            
            else:
                mally_log.error(f"❌ Error API Telegram ({response.status_code}): {response.text}")

        except Exception as e:
            mally_log.error(f"⚠️ Excepción en envío (intento {intentos+1}): {str(e)}")
        
        intentos += 1
        time.sleep(5) # Pausa breve entre reintentos

    return False
