import requests
import time
import os
import config
import threading

buffer_envio = {}
siguiente_esperado = 1
lock_envio = threading.Lock()
session = requests.Session()

def despachar_ordenado():
    global siguiente_esperado
    while siguiente_esperado in buffer_envio:
        ruta, caption = buffer_envio.pop(siguiente_esperado)
        
        # Reintentos automáticos
        for intento in range(config.REINTENTOS_ENVIO):
            if subir_a_telegram(ruta, caption):
                siguiente_esperado += 1
                break
            time.sleep(5) # Espera antes de reintentar

def subir_a_telegram(ruta, caption):
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
    try:
        with open(ruta, "rb") as v:
            payload = {"chat_id": config.CHAT_ID, "caption": caption, "supports_streaming": "true"}
            r = session.post(url, data=payload, files={"video": v}, timeout=config.TIMEOUT_TELEGRAM)
        
        if r.status_code == 200:
            print(f"[✅] Parte enviada y borrada: {os.path.basename(ruta)}")
            os.remove(ruta)
            return True
    except: pass
    return False

def encolar_para_telegram(ruta, caption, parte):
    with lock_envio:
        buffer_envio[parte] = (ruta, caption)
        despachar_ordenado()
