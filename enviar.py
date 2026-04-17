import requests # <- Cambiado de 'Import' a 'import' (minúscula)
import config
import threading
import time
import os

session = requests.Session()

# 🧠 Control de orden estricto
buffer_videos = {}
siguiente_parte = 1
lock = threading.Lock()

def esperar_archivo_listo(ruta, timeout=15):
    """Verifica que el archivo ya no esté creciendo (FFmpeg terminó)."""
    inicio = time.time()
    tamaño_anterior = -1
    while time.time() - inicio < timeout:
        if os.path.exists(ruta):
            tamaño_actual = os.path.getsize(ruta)
            if tamaño_actual > 0 and tamaño_actual == tamaño_anterior:
                return True
            tamaño_anterior = tamaño_actual
        time.sleep(0.5)
    return False

def enviar_video(ruta, caption):
    url = f"https://api.telegram.org/bot{config.TOKEN}/sendVideo"
    try:
        with open(ruta, "rb") as v:
            payload = {
                "chat_id": config.CHAT_ID,
                "caption": caption,
                "supports_streaming": "true"
            }
            r = session.post(url, data=payload, files={"video": v}, timeout=300)
        
        if r.status_code == 200:
            print(f"[✅] Enviado OK: {os.path.basename(ruta)}")
            if os.path.exists(ruta): os.remove(ruta)
            return True
        else:
            print(f"[❌] Error Telegram ({r.status_code}): {r.text}")
            return False
    except Exception as e:
        print(f"[⚠️] Error de red: {e}")
        return False

def intentar_enviar():
    """Busca en el buffer si la siguiente parte que toca ya está lista."""
    global siguiente_parte
    # IMPORTANTE: No usamos un 'while True' aquí para no bloquear el Lock eternamente
    while siguiente_parte in buffer_videos:
        ruta, caption = buffer_videos.pop(siguiente_parte)
        
        if esperar_archivo_listo(ruta):
            enviar_video(ruta, caption)
            siguiente_parte += 1
        else:
            # Si el archivo no está listo, lo devolvemos al buffer y paramos
            buffer_videos[siguiente_parte] = (ruta, caption)
            break

def encolar_video(ruta, caption, parte):
    """Función que llama el Main para meter clips a la fila."""
    with lock:
        buffer_videos[parte] = (ruta, caption)
        intentar_enviar()
