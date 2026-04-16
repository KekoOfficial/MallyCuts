import telebot
import config
import time
import psutil
import datetime

bot = telebot.TeleBot(config.BOT_TOKEN)

def get_sys_telemetry():
    """Captura de hardware en tiempo real."""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, ram, disk
    except: return 0, 0, 0

def create_bar(percent, length=12):
    """Barra visual sólida."""
    filled = int(length * percent // 100)
    return "█" * filled + "▒" * (length - filled)

def registrar_despliegue_imperial(nombre, descripcion, portada_path):
    cpu, ram, disk = get_sys_telemetry()
    header = "💠 ─── 𝖴𝖬𝖡𝖱𝖠𝖤 𝖲𝖸𝖲𝖳𝖤𝖬 𝖮𝖲 𝖵𝟨.𝟧 ─── 💠"
    
    msg = (
        f"{header}\n\n"
        f"📂 **PROYECTO:** `{nombre.upper()}`\n"
        f"📝 **INFO:** `{descripcion[:50]}...`\n"
        f"👑 **ADMIN:** `Noa`\n\n"
        f"📊 **MÉTRICAS:**\n"
        f"├─ CPU: `{create_bar(cpu)}` {cpu}%\n"
        f"├─ RAM: `{create_bar(ram)}` {ram}%\n"
        f"└─ DSK: `{create_bar(disk)}` {disk}%\n\n"
        f"🛰️ **SINC:** `{datetime.datetime.now().strftime('%H:%M:%S')} | @MallySeries`"
    )
    try:
        with open(portada_path, 'rb') as p:
            bot.send_photo(config.CHAT_ID, p, caption=msg, parse_mode='Markdown')
    except: pass

def notify_clip_sent(current, total, nombre):
    prog = int((current / total) * 100)
    msg = (f"🎬 **SEGMENTO:** `{current}/{total}`\n"
           f"📈 **STATUS:** `{create_bar(prog)}` {prog}%\n"
           f"📡 **NODO:** `TRANSFERENCIA EXITOSA`")
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass

def mision_cumplida(nombre, total):
    msg = (f"🏆 **OPERACIÓN FINALIZADA**\n"
           f"━━━━━━━━━━━━━━━━━━━━\n"
           f"👑 **PROYECTO:** `{nombre}`\n"
           f"✅ **CLIPS:** `{total}` | `STANDBY - UMBRAE`")
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass
