import subprocess
import re
import time
import os
import socket
import threading
import telebot
import config
from flask import Flask # Asegúrate de que tu lógica de Flask esté aquí o se importe

# --- IMPORTA AQUÍ TU APP DE FLASK ---
# Si tu Flask está en otro archivo, por ejemplo app.py:
# from app import app 
# Si está aquí mismo, define 'app = Flask(__name__)' abajo.

app = Flask(__name__) # Ejemplo, ajusta según tu código real

@app.route('/')
def home():
    return "Umbrae Studio Core Online"

# --- CONFIGURACIÓN DE MANDO ---
ADMIN_ID = "8630490789"
bot = telebot.TeleBot(config.BOT_TOKEN)

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def buscar_cl():
    rutas = ["/data/data/com.termux/files/usr/bin/cloudflared", os.path.expanduser("~/cloudflared")]
    for r in rutas:
        if os.path.exists(r): return r
    return "cloudflared"

def iniciar_tunel():
    """Esta función corre en un hilo separado"""
    print("⏳ Esperando estabilidad del servidor para abrir túnel...")
    time.sleep(5) # Espera a que Flask respire
    
    cl_path = buscar_cl()
    url_publica = None
    
    for intento in range(1, 6):
        if check_port(8000):
            print(f"🌍 [TUNEL] Intento {intento}: Conectando con Cloudflare...")
            proc = subprocess.Popen(
                [cl_path, "tunnel", "--url", "http://localhost:8000"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            
            start_t = time.time()
            while time.time() - start_t < 40:
                line = proc.stdout.readline()
                if not line: break
                match = re.search(r"https://[-a-zA-Z0-9\.]+trycloudflare\.com", line)
                if match:
                    url_publica = match.group(0)
                    break
            
            if url_publica:
                mensaje = (
                    f"👑 <b>UMBRAE STUDIO MASTER CORE</b>\n"
                    f"───────────────────\n"
                    f"🔗 <b>Link:</b> {url_publica}\n"
                    f"🚀 <b>Status:</b> Sincronizado\n"
                    f"───────────────────"
                )
                print(f"✅ URL GENERADA: {url_publica}")
                bot.send_message(ADMIN_ID, mensaje, parse_mode="HTML")
                break
            else:
                proc.terminate()
                print("⚠️ No se detectó URL, reintentando...")
                time.sleep(3)
        else:
            print(f"🔄 Puerto 8000 cerrado, reintentando... ({intento}/5)")
            time.sleep(3)

if __name__ == "__main__":
    # 1. Lanzamos el túnel en un hilo (Background)
    hilo_tunel = threading.Thread(target=iniciar_tunel, daemon=True)
    hilo_tunel.start()
    
    # 2. Lanzamos Flask en el hilo principal
    print("🚀 [CORE] Lanzando Servidor Flask en Puerto 8000...")
    try:
        # IMPORTANTE: host 0.0.0.0 y use_reloader=False para no duplicar hilos
        app.run(host="0.0.0.0", port=8000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n🛑 Apagando sistemas Umbrae...")
