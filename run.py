import subprocess
import re
import time
import os
import socket
import telebot
import config

# --- CONFIG ---
STAFF_IMPERIAL = {
    "ADMIN_PRINCIPAL": "8630490789",
    "FUNDADORES": ["8630490789"]
}

bot = telebot.TeleBot(config.BOT_TOKEN)

PORT = 8000
MAX_INTENTOS_TUNEL = 5
MAX_ESPERA_FLASK = 20


# --- UTILIDADES ---
def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def buscar_binario_cloudflared():
    rutas = [
        "/data/data/com.termux/files/usr/bin/cloudflared",
        os.path.expanduser("~/cloudflared"),
        "/usr/local/bin/cloudflared"
    ]

    for r in rutas:
        if os.path.exists(r) and os.access(r, os.X_OK):
            return r

    try:
        res = subprocess.run(["which", "cloudflared"], capture_output=True, text=True)
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass

    return None


def limpiar_proceso(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def enviar_notificacion(msg):
    for uid in STAFF_IMPERIAL["FUNDADORES"]:
        try:
            bot.send_message(uid, msg, parse_mode="HTML")
        except Exception as e:
            print(f"❌ Error Telegram: {e}")


# --- CORE ---
def lanzar_core_pro():
    server_proc = None
    tunnel_proc = None

    try:
        print("🚀 Iniciando servidor Flask...")

        log = open("server.log", "a")
        server_proc = subprocess.Popen(
            ["python", "server.py"],
            stdout=log,
            stderr=log
        )

        # --- Espera activa Flask ---
        print("🧪 Esperando Flask...")
        for i in range(MAX_ESPERA_FLASK):
            if server_proc.poll() is not None:
                print("❌ Flask se cerró inesperadamente.")
                return

            if check_port(PORT):
                print("✅ Flask activo")
                break

            print(f"⌛ Intento {i+1}/{MAX_ESPERA_FLASK}")
            time.sleep(1)
        else:
            print("❌ Flask nunca abrió el puerto.")
            return

        # --- Cloudflare ---
        cl_path = buscar_binario_cloudflared()
        if not cl_path:
            print("❌ cloudflared no encontrado.")
            return

        url_publica = None

        for intento in range(1, MAX_INTENTOS_TUNEL + 1):
            print(f"🌍 Túnel intento {intento}/{MAX_INTENTOS_TUNEL}")

            tunnel_proc = subprocess.Popen(
                [cl_path, "tunnel", "--url", f"http://localhost:{PORT}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            start = time.time()

            while time.time() - start < 40:
                if tunnel_proc.poll() is not None:
                    print("⚠️ Túnel murió solo")
                    break

                line = tunnel_proc.stdout.readline()

                if line:
                    print(f"[TUNNEL] {line.strip()}")

                    match = re.search(r"https://[-a-zA-Z0-9\.]+trycloudflare\.com", line)
                    if match:
                        url_publica = match.group(0)
                        break

            if url_publica:
                break

            limpiar_proceso(tunnel_proc)
            time.sleep(2)

        if not url_publica:
            print("❌ No se pudo generar URL.")
            return

        # --- Notificación ---
        mensaje = (
            f"👑 <b>UMBRAE CORE PRO</b>\n"
            f"───────────────────\n"
            f"🔗 <b>{url_publica}</b>\n"
            f"📡 ONLINE\n"
            f"⚙️ Puerto: {PORT}\n"
            f"───────────────────"
        )

        print(f"✅ URL: {url_publica}")
        enviar_notificacion(mensaje)

        # Mantener vivo
        tunnel_proc.wait()

    except KeyboardInterrupt:
        print("\n🛑 Apagando...")

    finally:
        limpiar_proceso(tunnel_proc)
        limpiar_proceso(server_proc)


if __name__ == "__main__":
    lanzar_core_pro()