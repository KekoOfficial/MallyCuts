import subprocess
import re
import time
import os
import telebot
import config

# --- GESTIÓN DE CREADORES & ADMIN ---
# ID Principal (Noa/Oliver) y Fundadores/Managers
STAFF_IMPERIAL = {
    "ADMIN_PRINCIPAL": "8630490789",
    "FUNDADORES": ["8630490789"] # Puedes agregar más IDs aquí
}

bot = telebot.TeleBot(config.BOT_TOKEN)

def buscar_binario_cloudflared():
    """Busca la ruta del binario para evitar el FileNotFoundError"""
    rutas_posibles = [
        "/data/data/com.termux/files/usr/bin/cloudflared",
        os.path.expanduser("~/cloudflared"),
        "cloudflared"
    ]
    for ruta in rutas_posibles:
        if subprocess.run(["which", ruta], capture_output=True).returncode == 0:
            return ruta
    return None

def lanzar_infraestructura():
    print("🚀 [UMBRAE CORE] Iniciando Servidor Flask...")
    
    # 1. Iniciar el servidor Mally Studio
    server_proc = subprocess.Popen(
        ["python", "server.py"], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    time.sleep(3) # Tiempo de carga del sistema
    
    print("🌍 [CLOUDFLARE] Sincronizando Túnel Seguro...")
    
    cl_path = buscar_binario_cloudflared()
    if not cl_path:
        print("❌ ERROR: No se encontró 'cloudflared'. Instálalo primero.")
        return

    # 2. Iniciar el túnel capturando logs
    tunnel_cmd = [cl_path, "tunnel", "--url", "http://localhost:8000"]
    tunnel_proc = subprocess.Popen(
        tunnel_cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT, 
        text=True
    )

    url_publica = None
    start_time = time.time()

    # 3. Extracción inteligente de la URL
    while time.time() - start_time < 45:
        line = tunnel_proc.stdout.readline()
        if not line: break
        
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url_publica = match.group(0)
            break
            
    if url_publica:
        # Notificación para el Staff Imperial
        mensaje = (
            f"👑 <b>UMBRAE STUDIO • CORE V2</b>\n"
            f"───────────────────\n"
            f"🚀 <b>Servidor:</b> ONLINE\n"
            f"🔗 <b>URL Pública:</b> {url_publica}\n"
            f"🛠️ <b>Admin:</b> Noa\n"
            f"───────────────────\n"
            f"📱 <i>Acceso total al Panel Mally habilitado.</i>"
        )
        
        print(f"✅ SISTEMA ACTIVO: {url_publica}")
        
        # Enviar a todos los fundadores
        for user_id in STAFF_IMPERIAL["FUNDADORES"]:
            try:
                bot.send_message(user_id, mensaje, parse_mode="HTML")
            except Exception as e:
                print(f"⚠️ No se pudo notificar al ID {user_id}: {e}")
    else:
        error_msg = "❌ CRÍTICO: El túnel no respondió a tiempo."
        print(error_msg)
        bot.send_message(STAFF_IMPERIAL["ADMIN_PRINCIPAL"], error_msg)

    try:
        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 [UMBRAE] Desconectando protocolos...")
        server_proc.terminate()
        tunnel_proc.terminate()

if __name__ == "__main__":
    lanzar_infraestructura()
