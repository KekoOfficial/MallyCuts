import subprocess
import re
import time
import os
import socket
import telebot
import config
import signal

# --- CONFIGURACIÓN DE MANDO ---
STAFF_IMPERIAL = {
    "ADMIN_PRINCIPAL": "8630490789",
    "FUNDADORES": ["8630490789"] 
}

bot = telebot.TeleBot(config.BOT_TOKEN)
MAX_INTENTOS_TUNEL = 5

def check_port(port):
    """Verifica si el servidor Flask realmente despertó"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def buscar_binario_cloudflared():
    """Búsqueda lógica basada en existencia de archivos"""
    rutas = [
        "/data/data/com.termux/files/usr/bin/cloudflared",
        os.path.expanduser("~/cloudflared"),
        "/usr/local/bin/cloudflared"
    ]
    for r in rutas:
        if os.path.exists(r) and os.access(r, os.X_OK):
            return r
    # Fallback al PATH
    try:
        res = subprocess.run(["which", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
    except: pass
    return None

def limpiar_proceso(proc):
    """Evita la creación de procesos zombis"""
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

def lanzar_core_pro():
    server_proc = None
    tunnel_proc = None
    
    try:
        print("🚀 [UMBRAE] Iniciando Servidor...")
        # Logs reales para auditoría
        with open("server.log", "a") as log:
            server_proc = subprocess.Popen(["python", "server.py"], stdout=log, stderr=log)
        
        # 1. Esperar a que Flask esté listo (Watchdog de puerto)
        intentos_port = 0
        while not check_port(8000) and intentos_port < 10:
            time.sleep(1)
            intentos_port += 1
        
        if intentos_port == 10:
            print("❌ Error: Flask no arrancó en el puerto 8000.")
            return

        cl_path = buscar_binario_cloudflared()
        if not cl_path:
            print("❌ Error: cloudflared no detectado.")
            return

        url_publica = None
        intentos_t = 0
        
        # 2. Bucle de Túnel con límite y limpieza
        while not url_publica and intentos_t < MAX_INTENTOS_TUNEL:
            intentos_t += 1
            print(f"🌍 [TUNEL] Intento {intentos_t}/{MAX_INTENTOS_TUNEL}...")
            
            tunnel_proc = subprocess.Popen(
                [cl_path, "tunnel", "--url", "http://localhost:8000"], 
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                bufsize=1, universal_newlines=True
            )

            # Lectura con timeout lógico
            start_t = time.time()
            while time.time() - start_t < 40:
                line = tunnel_proc.stdout.readline()
                if not line: break
                
                # Regex mejorada para subdominios complejos
                match = re.search(r"https://[-a-zA-Z0-9\.]+trycloudflare\.com", line)
                if match:
                    url_publica = match.group(0)
                    break
            
            if not url_publica:
                print("⚠️ Fallo en este intento. Limpiando...")
                limpiar_proceso(tunnel_proc)
                time.sleep(2)

        if url_publica:
            mensaje = (
                f"👑 <b>CORE PRO UMBRAE ACTIVO</b>\n"
                f"───────────────────\n"
                f"🔗 <b>Link:</b> {url_publica}\n"
                f"📡 <b>Status:</b> Sincronizado\n"
                f"⚙️ <b>Puerto:</b> 8000 (Open)\n"
                f"───────────────────"
            )
            print(f"✅ URL: {url_publica}")
            for uid in STAFF_IMPERIAL["FUNDADORES"]:
                try: bot.send_message(uid, mensaje, parse_mode="HTML")
                except Exception as e: print(f"Error Notify: {e}")
            
            # Mantener vivo el túnel
            tunnel_proc.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Apagando Infraestructura...")
    finally:
        limpiar_proceso(tunnel_proc)
        limpiar_proceso(server_proc)

if __name__ == "__main__":
    lanzar_core_pro()
