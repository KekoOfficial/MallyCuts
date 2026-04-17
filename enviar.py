import os
import time
import requests
import config

def worker_telegram():
    while True:
        tarea = cola_envio.get()
        ruta, caption = tarea
        
        # ESPERA ACTIVA: Espera hasta 10 segundos a que el archivo aparezca
        intentos = 0
        while not os.path.exists(ruta) and intentos < 10:
            time.sleep(1) 
            intentos += 1

        if os.path.exists(ruta):
            try:
                url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
                with open(ruta, "rb") as v:
                    r = requests.post(url, data={
                        "chat_id": config.CHAT_ID,
                        "caption": caption,
                        "supports_streaming": "true"
                    }, files={"video": v}, timeout=300)
                
                if r.status_code == 200:
                    os.remove(ruta) # Borrar solo si se envió bien
                else:
                    print(f"❌ Error API Telegram: {r.text}")
            except Exception as e:
                print(f"❌ Error enviando {ruta}: {e}")
        else:
            print(f"💀 EL ARCHIVO NUNCA SE CREÓ: {ruta}. Revisa si FFmpeg falló.")
            
        cola_envio.task_done()
