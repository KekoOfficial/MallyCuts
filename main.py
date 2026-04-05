# 1. INFRAESTRUCTURA Y SEGURIDAD
import os, subprocess, threading, time
from contextlib import ExitStack
from flask import Flask, render_template_string, request
from telebot import TeleBot, apihelper
import config

# Configuración Maestra de Red
apihelper.READ_TIMEOUT = config.READ_TIMEOUT
apihelper.CONNECT_TIMEOUT = config.CONNECT_TIMEOUT
bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# 2. UTILIDADES
def limpiar_nombre(texto):
    """Limpia el nombre para carpetas y mensajes HTML."""
    return "".join(c for c in texto if c.isalnum() or c in (' ', '-', '_')).strip()

# 3. EL DESPACHADOR (ENVÍO EN TIEMPO REAL)
def despachador_de_clips(serie_folder, nombre_bonito, total_esperado):
    """Busca clips y los envía con estética PREMIUM mientras se procesan."""
    enviados = 0
    
    # --- MENSAJE DE INICIO ÉPICO ---
    bot.send_message(config.CHAT_ID, f"""
🎬 <b>MALLY SERIES</b>

🚀 <b>INICIANDO PRODUCCIÓN</b>

📂 <b>{nombre_bonito}</b>

⏳ <i>Preparando episodios...</i>
""", parse_mode="HTML")

    while enviados < total_esperado:
        clips_disponibles = sorted([f for f in os.listdir(serie_folder) if f.startswith('ep_') and f.endswith('.mp4')])
        
        if len(clips_disponibles) > 1 or (enviados == total_esperado - 1 and len(clips_disponibles) == 1):
            clip_name = clips_disponibles[0]
            path_v = os.path.join(serie_folder, clip_name)
            path_t = path_v.replace(".mp4", ".jpg")
            enviados += 1

            # Crear Miniatura
            subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)
            
            # --- CAPTION ULTRA PREMIUM ---
            caption = f"""
🎬 <b>MALLY SERIES</b>

╔════════════════════╗
  ▶️ <i>Now Playing</i>
╚════════════════════╝

📂 <b>{nombre_bonito}</b>
💎 <b>Parte {enviados}/{total_esperado}</b>
📡 <b>@MallySeries</b>

═══════ ✦ ═══════
🔥 <b>EN EMISIÓN</b>
═══════ ✦ ═══════
"""

            # Bucle de Reintentos
            for intento in range(1, config.MAX_RETRIES + 1):
                try:
                    with ExitStack() as stack:
                        v = stack.enter_context(open(path_v, 'rb'))
                        t = stack.enter_context(open(path_t, 'rb')) if os.path.exists(path_t) else None
                        bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML", timeout=config.READ_TIMEOUT)
                    print(f"✅ Premium Send: {clip_name}")
                    break
                except Exception as e:
                    print(f"⚠️ Reintento {intento}: {e}")
                    time.sleep(10)

            if os.path.exists(path_v): os.remove(path_v)
            if os.path.exists(path_t): os.remove(path_t)
            time.sleep(2) 
        else:
            time.sleep(4)

    # --- MENSAJE FINAL PREMIUM ---
    bot.send_message(config.CHAT_ID, f"""
🎬 <b>MALLY SERIES</b>

📂 <b>{nombre_bonito}</b>

──────── ✦ ────────
🏁 <b>TEMPORADA COMPLETA</b>
──────── ✦ ────────

🌙 <i>Cada final… es un nuevo comienzo</i>
""", parse_mode="HTML")

    try: os.rmdir(serie_folder)
    except: pass

# 4. EL MOTOR (CORTADOR DINÁMICO)
def motor_mally_pro(video_path, original_name):
    nombre_limpio = limpiar_nombre(original_name)
    serie_folder = os.path.join(config.TEMP_FOLDER, nombre_limpio.replace(" ", "_"))
    
    if not os.path.exists(serie_folder): os.makedirs(serie_folder)

    # FFprobe para saber el final
    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path])
    total_esperado = int(float(probe) // config.CLIP_DURATION) + 1

    hilo_envio = threading.Thread(target=despachador_de_clips, args=(serie_folder, nombre_limpio, total_esperado))
    hilo_envio.start()

    output_pattern = os.path.join(serie_folder, "ep_%03d.mp4")
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, 
            '-f', 'segment', '-segment_time', str(config.CLIP_DURATION),
            '-reset_timestamps', '1', '-c', 'copy', output_pattern
        ], check=True)
    except Exception as e:
        print(f"❌ Error FFmpeg: {e}")

    hilo_envio.join()
    if os.path.exists(video_path): os.remove(video_path)

# 5. INTERFAZ WEB (MISMA LÓGICA)
@app.route('/')
def index():
    return render_template_string('''
    <body style="background:#000;color:#e50914;text-align:center;padding-top:100px;font-family:sans-serif;">
        <h1 style="font-size:3em;">MALLY <span style="color:#fff">PRO</span></h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label style="background:#e50914;color:#fff;padding:20px 40px;cursor:pointer;font-weight:bold;border-radius:50px;box-shadow: 0 0 20px #e50914;">
                SUBIR SERIE
                <input type="file" name="file" accept="video/*" onchange="this.form.submit()" style="display:none;">
            </label>
        </form>
    </body>''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = "input_pro.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_pro, args=(save_path, file.filename)).start()
    return "<h1>🚀 Producción en tiempo real iniciada...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
