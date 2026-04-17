import requests
import config
import queue
import threading
import time
import os

# 1. Creamos la cola
cola_envio = queue.Queue()

def worker_telegram():
    while True:
        # Extrae la tarea de la cola
        ruta, caption = cola_envio.get()
        
        # Espera un poco a que el archivo termine de escribirse en disco
        intentos = 0
        while not os.path.exists(ruta) and intentos < 10:
            time.sleep(1)
            intentos += 1

        if os.path.exists(ruta):
            try:
                url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
                with open(ruta, "rb") as v:
                    payload = {
                        "chat_id": config.CHAT_ID, 
                        "caption": caption, 
                        "supports_streaming": "true"
                    }
                    r = requests.post(url, data=payload, files={"video": v}, timeout=300)
                
                if r.status_code == 200:
                    print(f"[✅] Enviado: {os.path.basename(ruta)}")
                    os.remove(ruta) # Borra el clip enviado para ahorrar espacio
                else:
                    print(f"[❌] Error API ({r.status_code}): {r.text}")
            except Exception as e:
                print(f"[❌] Error de conexión: {e}")
        else:
            print(f"[💀] No se encontró el archivo tras 10s: {ruta}")
            
        cola_envio.task_done()

# 2. Iniciamos el hilo de envío (solo uno para mantener el orden)
threading.Thread(target=worker_telegram, daemon=True).start()

# 3. ESTA ES LA FUNCIÓN QUE TE FALTA
def encolar_video(ruta, caption):
    """Añade un video a la fila de espera para ser enviado."""
    cola_envio.put((ruta, caption))
