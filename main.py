# 1. INFRAESTRUCTURA
import os, subprocess, threading, time
from contextlib import ExitStack
from flask import Flask, render_template_string, request
from telebot import TeleBot, apihelper
import config

apihelper.READ_TIMEOUT = config.READ_TIMEOUT
apihelper.CONNECT_TIMEOUT = config.CONNECT_TIMEOUT
bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

def limpiar_nombre(texto):
    # Eliminar extensiones y caracteres que rompen carpetas
    return "".join(c for c in texto if c.isalnum() or c in (' ', '-', '_')).strip()

# 2. EL DESPACHADOR (CON TÍTULO PROFESIONAL)
def despachador_de_clips(serie_folder, nombre_bonito, total_esperado):
    enviados = 0
    
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

            subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)
            
            # ELIMINAMOS NÚMEROS DE ARCHIVO - SOLO TÍTULO Y PARTE
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

            for intento in range(1, config.MAX_RETRIES + 1):
                try:
                    with ExitStack() as stack:
                        v = stack.enter_context(open(path_v, 'rb'))
                        t = stack.enter_context(open(path_t, 'rb')) if os.path.exists(path_t) else None
                        bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML", timeout=config.READ_TIMEOUT)
                    break
                except Exception as e:
                    time.sleep(10)

            if os.path.exists(path_v): os.remove(path_v)
            if os.path.exists(path_t): os.remove(path_t)
            time.sleep(2) 
        else:
            time.sleep(4)

    bot.send_message(config.CHAT_ID, f"""
🎬 <b>MALLY SERIES</b>

📂 <b>{nombre_bonito}</b>

──────── ✦ ────────
🏁 <b>TEMPORADA COMPLETA</b>
──────── ✦ ────────

🌙 <i>Cada final… es un nuevo comienzo</i>
""", parse_mode="HTML")

# 3. MOTOR (RECIBE EL TÍTULO MANUAL)
def motor_mally_pro(video_path, nombre_final):
    nombre_limpio = limpiar_nombre(nombre_final)
    serie_folder = os.path.join(config.TEMP_FOLDER, nombre_limpio.replace(" ", "_"))
    
    if not os.path.exists(serie_folder): os.makedirs(serie_folder)

    probe = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path])
    total_esperado = int(float(probe) // config.CLIP_DURATION) + 1

    threading.Thread(target=despachador_de_clips, args=(serie_folder, nombre_limpio, total_esperado)).start()

    output_pattern = os.path.join(serie_folder, "ep_%03d.mp4")
    try:
        subprocess.run(['ffmpeg', '-y', '-i', video_path, '-f', 'segment', '-segment_time', str(config.CLIP_DURATION), '-reset_timestamps', '1', '-c', 'copy', output_pattern], check=True)
    except: pass

# 4. INTERFAZ WEB MEJORADA
@app.route('/')
def index():
    return render_template_string('''
    <body style="background:#000;color:#fff;text-align:center;padding-top:50px;font-family:sans-serif;">
        <h1 style="color:#e50914; font-size:3.5em; margin-bottom:0;">MALLY PRO</h1>
        <p style="color:#888; letter-spacing:2px;">STUDIO EDITION</p>
        
        <form action="/upload" method="post" enctype="multipart/form-data" style="margin-top:40px;">
            <input type="text" name="titulo" placeholder="Nombre de la Serie (Ej: Mi Camino a Ti)" 
                   style="width:80%; max-width:400px; padding:15px; border-radius:10px; border:1px solid #333; background:#111; color:#fff; margin-bottom:20px; font-size:16px;">
            <br>
            <label style="background:#e50914; color:#fff; padding:20px 40px; cursor:pointer; font-weight:bold; border-radius:10px; display:inline-block; box-shadow: 0 10px 20px rgba(229,9,20,0.3);">
                SELECCIONAR VIDEO
                <input type="file" name="file" accept="video/*" onchange="this.form.submit()" style="display:none;">
            </label>
        </form>
    </body>''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    titulo_manual = request.form.get('titulo')
    # Si no escribes nada, usa el nombre del archivo pero quita el ".mp4"
    nombre_final = titulo_manual if titulo_manual else file.filename.rsplit('.', 1)[0]
    
    save_path = "input_pro.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_pro, args=(save_path, nombre_final)).start()
    return "<h1>🚀 Producción Iniciada...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
