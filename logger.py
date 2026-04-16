import telebot, config, psutil, datetime

bot = telebot.TeleBot(config.BOT_TOKEN)

def get_sys():
    """Telemetría compacta del núcleo."""
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"⚡ `{cpu}%` 💠 `{ram}%`"
    except: return "💮 `ONLINE`"

def generar_caption(nombre, actual, total):
    """Post oficial para @MallySeries."""
    return (
        f"🎬 {nombre}\n"
        f"💎 CAPÍTULO: {actual} / {total}\n"
        f"✅ Contenido Verificado\n"
        f"🔗 @MallySeries #UmbraeStudio"
    )

def registrar_despliegue_imperial(nombre, descripcion, portada_path):
    # Encabezado de alta estética
    header = "╭━━━ ⋅💠⋅ ━━━╮\n  𝗦𝗔𝗞𝗨𝗥𝗔 𝗦𝗬𝗦𝗧𝗘𝗠\n╰━━━ ⋅💠⋅ ━━━╯"
    msg = (
        f"{header}\n\n"
        f"🌸 **𝗠𝗜𝗦𝗜𝗢𝗡:** `{nombre.upper()}`\n"
        f"👑 **𝗗𝗘𝗩:** `@OliDevX`\n"
        f"📈 **𝗡𝗨𝗖𝗟𝗘𝗢:** {get_sys()}\n\n"
        f"✨ `Inyectando pétalos al motor...`"
    )
    try:
        with open(portada_path, 'rb') as p:
            bot.send_photo(config.CHAT_ID, p, caption=msg, parse_mode='Markdown')
    except: pass

def notify_clip_sent(current, total, nombre):
    # Formato ultra-estético para cada corte
    msg = (
        f"💮 **{nombre}**\n"
        f"╰─➤ 𝗖𝗼𝗿𝘁𝗲𝘀: `{current}/{total}` ✨ `Verificado`\n"
        f"🌸 `@MallySeries`"
    )
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass

def mision_cumplida(nombre, total):
    # Cierre elegante
    msg = (
        f"🌸 **𝗠𝗜𝗦𝗜𝗢𝗡 𝗖𝗢𝗡𝗖𝗟𝗨𝗜𝗗𝗔** 🌸\n"
        f"┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
        f"💮 `{nombre}` archivado.\n"
        f"🎀 `{total}` segmentos listos.\n"
        f"✨ **𝗗𝗲𝘃:** `@OliDevX`"
    )
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass

def log_error(e):
    msg = f"💔 **𝗦𝗬𝗦𝗧𝗘𝗠 𝗙𝗔𝗨𝗟𝗧**\n╰─➤ `{e}`\n🌸 `@OliDevX`"
    try: bot.send_message(config.CHAT_ID, msg, parse_mode='Markdown')
    except: pass
