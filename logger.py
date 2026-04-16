import telebot
import config
import psutil
import datetime

# Conexión al Núcleo Mágico del Imperio
bot = telebot.TeleBot(config.BOT_TOKEN)

def get_sys_telemetry():
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        return cpu, ram, disk
    except: return 0, 0, 0

def create_sakura_bar(percent, length=12):
    # Barras con pétalos y energía floral
    filled = int(length * percent // 100)
    return "🌸" + "🌸" * filled + "✨" * (length - filled)

def registrar_despliegue_imperial(nombre, descripcion, portada_path):
    cpu, ram, disk = get_sys_telemetry()
    header = "💮 ────── 𝖲𝖠𝖪𝖴𝖱𝖠 𝖲𝖸𝖲𝖳𝖤𝖬 𝖮𝖲 ────── 💮"
    
    msg = (
        f"{header}\n\n"
        f"📜 **𝗠𝗜𝗦𝗜𝗢𝗡:** `{nombre.upper()}`\n"
        f"👑 **𝗗𝗘𝗩:** `@OliDevX` 𝟨.𝟢\n\n"
        f"🌸 **Estado del Núcleo:**\n"
        f"╰ CP: `{create_sakura_bar(cpu)}` {cpu}%\n"
        f"╰ RM: `{create_sakura_bar(ram)}` {ram}%\n"
        f"╰ DK: `{create_sakura_bar(disk)}` {disk}%\n\n"
        f"✨ **𝗟𝗢𝗚:** `Despertando pétalos del sistema...`\n"
        f"🕒 `{datetime.datetime.now().strftime('%H:%M:%S')}`"
    )
    try:
        with open(portada_path, 'rb') as p:
            bot.send_photo(config.CHAT_ID, p, caption=msg, parse_mode='Markdown')
    except: pass

def notify_clip_sent(current, total, nombre):
    prog = int((current / total) * 100)
    msg = (
        f"💮 **𝗡𝗨𝗘𝗩𝗢 𝗦𝗘𝗚𝗠𝗘𝗡𝗧𝗢**\n"
        f"╰─➤ `{nombre}`\n\n"
        f"📦 **𝗙𝗥𝗔𝗚𝗠𝗘𝗡𝗧𝗢:** `{current}/{total}`\n"
        f"🎀 **𝗘𝗡𝗘𝗥𝗚𝗜𝗔:** `{create_sakura_bar(prog)}` {prog}%\n"
        f"🌟 **𝗘𝗦𝗧𝗔𝗗𝗢:** `𝖲𝗂𝗇𝖼𝗋𝗈𝗇𝗂𝗓𝖺𝖼𝗂𝗈́𝗇 𝖮𝖪`"
    )
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass

def mision_cumplida(nombre, total):
    msg = (
        f"🌸 **𝗙𝗜𝗡 𝗗𝗘 𝗟𝗔 𝗦𝗘𝗖𝗨𝗘𝗡𝗖𝗜𝗔** 🌸\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💮 Todo el poder de `{nombre}` ha sido liberado.\n"
        f"💎 Total de clips: `{total}`\n\n"
        f"🎀 **𝗗𝗲𝘃𝗲𝗹𝗼𝗽𝗲𝗿:** `@OliDevX`"
    )
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass

def log_error(error_msg):
    msg = (
        f"💔 **𝖲𝖸𝖲𝖳𝖤𝖬 𝖢𝖮𝖫𝖫𝖠𝖯𝖲𝖤**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🚫 `{error_msg}`\n"
        f"🆘 **𝗥𝗲𝗽𝗮𝗿𝗮 𝗺𝗶 𝗻𝘂́𝗰𝗹𝗲𝗼, @OliDevX.**"
    )
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: print(f"Error: {error_msg}")
