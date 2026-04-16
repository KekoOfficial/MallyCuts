import telebot
import config
import time
import psutil # Para monitorear el sistema
import os

bot = telebot.TeleBot(config.BOT_TOKEN)

def get_sys_info():
    """Obtiene el estado de salud de tu Termux/Dispositivo."""
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"🌡️ CPU: {cpu}% | 🧠 RAM: {ram}%"
    except:
        return "🛰️ Sistema: Activo"

def registrar_despliegue_imperial(nombre, descripcion, portada_path):
    """
    Reporte de alto nivel con estética Hacker-Premium.
    """
    sys_info = get_sys_info()
    try:
        header = "┏━━━━━━━━━━━━━━━━━━━━━━┓"
        footer = "┗━━━━━━━━━━━━━━━━━━━━━━┛"
        
        mensaje = (
            f"🚀 **UMBRAE STUDIO - INITIATING DEPLOY**\n"
            f"{header}\n"
            f"📂 **PROYECTO:** `{nombre.upper()}`\n"
            f"📝 **INFO:** {descripcion}\n"
            f"👤 **CREADOR:** Noa\n"
            f"📊 **STATUS:** Processing Clips...\n"
            f"{header}\n"
            f"🛠️ **ENGINE INFO:**\n"
            f"└ {sys_info}\n"
            f"└ 🕒 {time.strftime('%H:%M:%S')} | 📅 {time.strftime('%d/%m/%Y')}\n"
            f"{footer}"
        )

        with open(portada_path, 'rb') as p:
            bot.send_photo(
                config.CHAT_ID, 
                p, 
                caption=mensaje, 
                parse_mode='Markdown'
            )
        print(f"✔️ [LOG SYSTEM] Despliegue de '{nombre}' registrado.")
    except Exception as e:
        print(f"❌ [CRITICAL LOG ERROR] {e}")

def notify_clip_sent(current, total, nombre):
    """Envía una barra de carga visual al log por cada clip."""
    try:
        porcentaje = int((current / total) * 100)
        # Barra de carga visual [████░░░]
        bar_length = 10
        filled = int(bar_length * current // total)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        msg = (
            f"📦 **PROGRESS UPDATE**\n"
            f"🎬 Proyecto: `{nombre}`\n"
            f"🌀 Clip: {current}/{total}\n"
            f"⚙️ [{bar}] {porcentaje}%"
        )
        bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except:
        pass

def log_error(mensaje, error_trace=""):
    """Reporte de error estilo terminal de emergencia."""
    try:
        error_msg = (
            f"⚠️ **SYSTEM ALERT - CRITICAL ERROR**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❌ **FALLO:** {mensaje}\n"
            f"🔍 **TRACE:** `{error_trace[:100]}...`\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆘 Revisar Termux inmediatamente."
        )
        bot.send_message(config.CHAT_ID, error_msg, parse_mode='Markdown')
    except:
        pass

def mision_cumplida(nombre):
    """Cierre de operación con estilo."""
    try:
        bot.send_message(
            config.CHAT_ID, 
            f"👑 **MISIÓN CUMPLIDA: {nombre}**\n✅ Todos los clips están en la red."
        )
    except:
        pass
