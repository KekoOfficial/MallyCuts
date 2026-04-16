import subprocess
import re
import time
import telebot
import config

# Configuración de creadores
ADMIN_ID = "8630490789"
bot = telebot.TeleBot(config.BOT_TOKEN)

def lanzar_infraestructura():
    print("🚀 [UMBRAE CORE] Iniciando Servidor Flask...")
    # 1. Lanzar el servidor en segundo plano
    server_proc = subprocess.Popen(["python", "server.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
    
    time.sleep(2) # Espera a que el puerto 8000 esté listo
    
    print("🌍 [CLOUDFLARE] Generando Túnel Público...")
    # 2. Lanzar el túnel y capturar la salida para extraer la URL
    tunnel_cmd = ["cloudflared", "tunnel", "--url", "http://localhost:8000"]
    tunnel_proc = subprocess.Popen(tunnel_cmd, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT, 
                                    text=True)

    url_publica = None
    
    # 3. Escanear la salida en tiempo real para encontrar el link .trycloudflare.com
    start_time = time.time()
    while time.time() - start_time < 30: # Timeout de 30 segundos
        line = tunnel_proc.stdout.readline()
        if not line: break
        
        # Buscar el patrón de la URL
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            url_publica = match.group(0)
            break
            
    if url_publica:
        mensaje = (
            f"👑 <b>UMBRAE STUDIO • ONLINE</b>\n\n"
            f"🚀 Servidor sincronizado con éxito.\n"
            f"🔗 <b>Link de Acceso:</b> {url_publica}\n\n"
            f"📱 <i>Panel de Control Mally Series listo.</i>"
        )
        print(f"✅ URL Generada: {url_publica}")
        bot.send_message(ADMIN_ID, mensaje, parse_mode="HTML")
    else:
        print("❌ Error al obtener el túnel de Cloudflare.")
        bot.send_message(ADMIN_ID, "⚠️ Error crítico: No se pudo generar el túnel Cloudflare.")

    try:
        # Mantener el proceso vivo
        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 [UMBRAE] Apagando sistemas...")
        server_proc.terminate()
        tunnel_proc.terminate()

if __name__ == "__main__":
    lanzar_infraestructura()
