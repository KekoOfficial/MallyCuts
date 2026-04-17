import requests
import config
import queue
import threading
import time

# La cola mágica
cola_envio = queue.Queue()

def worker_telegram():
    while True:
        # Obtiene el paquete (ruta del video y su caption)
        tarea = cola_envio.get()
        ruta, caption = tarea
        
        try:
            url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
            with open(ruta, "rb") as v:
                requests.post(url, data={
                    "chat_id": config.CHAT_ID,
                    "caption": caption,
                    "supports_streaming": "true"
                }, files={"video": v}, timeout=300)
            
            # Limpieza post-envío
            import os
            if os.path.exists(ruta): os.remove(ruta)
            
        except Exception as e:
            print(f"❌ Error enviando {ruta}: {e}")
            # Reintento simple: si falla, vuelve a la cola al final
            # cola_envio.put(tarea) 
            
        cola_envio.task_done()
        time.sleep(1) # Respiro para evitar ban de Telegram

# Iniciamos el hilo de envío único (solo 1 a la vez)
threading.Thread(target=worker_telegram, daemon=True).start()

def encolar_video(ruta, caption):
    cola_envio.put((ruta, caption))
