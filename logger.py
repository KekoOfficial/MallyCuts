import telebot
import config
import time
import psutil
import os
import datetime

# Inicialización del Núcleo Imperial
bot = telebot.TeleBot(config.BOT_TOKEN)

def get_sys_telemetry():
    """Captura de datos de hardware en tiempo real (Xiaomi/Termux)."""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, ram, disk
    except:
        return 0, 0, 0

def create_bar(percent, length=12):
    """Barra de carga visual con estética de bloque sólido."""
    filled = int(length * percent // 100)
    return "█" * filled + "▒" * (length - filled)

def registrar_despliegue_imperial(nombre, descripcion, portada_path):
    """
    Envía la Ficha Técnica con telemetría de hardware al iniciar el proceso.
    """
    cpu, ram, disk = get_sys_telemetry()
    time_now = datetime.datetime.now().strftime('%H:%M:%S')
    
    header = "💠 ─── 𝖴𝖬𝖡𝖱𝖠𝖤 𝖲𝖸𝖲𝖳𝖤𝖬 𝖮𝖲 𝖵𝟨.𝟧 ─── 💠"
    
    # Acortamos la descripción para el log si es muy larga
    desc_corta = (descripcion[:60] + '...') if len(descripcion) > 60 else descripcion
    
    mensaje = (
        f"{header}\n\n"
        f"📂 **PROYECTO:** `{nombre.upper()}`\n"
        f"📝 **INFO:** `{desc_corta}`\n"
        f"👑 **OPERADOR:** `UmbraeStudio`\n\n"
        f"📊 **MÉTRICAS DEL SISTEMA:**\n"
        f"├─ CPU: `{create_bar(cpu)}` {cpu}%\n"
        f"├─ RAM: `{create_bar(ram)}` {ram}%\n"
        f"└─ DSK: `{create_bar(disk)}` {disk}%\n\n"
        f"🛰️ **SINC:** `{time_now} | @MallySeries`"
    )

    try:
        with open(portada_path, 'rb') as p:
            bot.send_photo(config.CHAT_ID, p, caption=mensaje, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(config.CHAT_ID, f"⚠️ **ALERTA:** No se pudo cargar la portada.\n`{e}`")

def notify_clip_sent(current, total, nombre):
    """Reporte individual por cada segmento de video enviado."""
    prog = int((current / total) * 100)
    
    msg = (
        f"🎬 **SEGMENTO PROCESADO**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 **LOTE:** `{current}/{total}`\n"
        f"📈 **STATUS:** `{create_bar(prog)}` {prog}%\n"
        f"💠 **ID:** `{nombre}`\n"
        f"📡 **NODO:** `TRANSFERENCIA COMPLETA`"
    )
    try:
        bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except:
        pass

def mision_cumplida(nombre, total):
    """Cierre oficial de la operación de carga."""
    final_msg = (
        f"🏆 **OPERACIÓN FINALIZADA**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 **PROYECTO:** `{nombre}`\n"
        f"✅ **CLIPS:** `{total} Unidades`\n"
        f"🔌 **ESTADO:** `STANDBY - UMBRAE`"
    )
    try:
        bot.send_message(config.CHAT_ID, final_msg, parse_mode='Markdown')
    except:
        pass

def log_error(error_msg):
    """Notificación de fallo crítico."""
    error_report = (
        f"🚫 **ERROR DE KERNEL**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛑 **FALLO:** `{error_msg}`\n"
        f"🆘 **ACCIÓN:** Revisar logs en Termux."
    )
    try:
        bot.send_message(config.CHAT_ID, error_report, parse_mode='Markdown')
    except:
        pass
