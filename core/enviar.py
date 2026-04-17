import requests
import time
import os
from config import *
from core.logger import log

session = requests.Session()

def enviar_a_telegram(ruta_archivo, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    
    for intento in range(REINTENTOS_ENVIO):
        try:
            with open(ruta_archivo, "rb") as f:
                respuesta = session.post(
                    url,
                    data={
                        "chat_id": CHAT_ID,
                        "caption": caption,
                        "supports_streaming": True
                    },
                    files={"video": f},
                    timeout=TIMEOUT_TELEGRAM
                )
            
            if respuesta.status_code == 200:
                log.info(f"✅ Enviado correctamente")
                os.remove(ruta_archivo)
                time.sleep(PAUSA_ENTRE_ENVIOS)
                return True
            elif respuesta.status_code == 429:
                espera = int(respuesta.json().get('parameters', {}).get('retry_after', 10))
                log.warning(f"🔁 Muy rápido, esperando {espera}s...")
                time.sleep(espera)
            else:
                log.warning(f"⚠️ Código {respuesta.status_code} - Intento {intento+1}")
                time.sleep(5)
                
        except Exception as e:
            log.error(f"📡 Error conexión: {e}")
            time.sleep(5)
    
    log.error(f"❌ Falló envío después de {REINTENTOS_ENVIO} intentos")
    return False
