import os
import subprocess
import threading
import time
import json
from contextlib import ExitStack
from flask import Flask, render_template_string, request
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# --- UTILIDADES ---
def limpiar_html(texto):
    return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# --- MOTOR DE PRODUCCIÓN ---
def motor_mally_pro(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    nombre_seguro = limpiar_html(original_name)
    
    # PROTECCIÓN: Si CLIP_DURATION no existe en config, usa 60 por defecto
    segundos_corte = getattr(config, 'CLIP_DURATION', 60)
    
    # 1. FFmpeg Segmentación
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, 
            '-f', 'segment', '-segment_time', str(segundos_corte),
            '-reset_timestamps', '1', '-c', 'copy', output_pattern
        ], check=True)
    except Exception as e:
        print(f"❌ Error en FFmpeg: {e}")
        return

    clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
    
    bot.send_message(config.CHAT_ID, f"🎬 <b>PRODUCCIÓN INICIADA</b>\n<b>Serie:</b> {nombre_seguro}\n<b>Episodios:</b> {len(clips)}", parse_mode="HTML")

    # 2. Ciclo de Envío
    for i, clip_name in enumerate(clips, 1):
        path_v = os.path.join(config.TEMP_FOLDER, clip_name)
        path_t = path_v.replace(".mp4", ".jpg")
        
        # Thumbnail
        subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)

        with ExitStack() as stack:
            v = stack.enter_context(open(path_v, 'rb'))
            t = stack.enter_context(open(path_t, 'rb')) if os.path.exists(path_t) else None

            caption = f"🎬 <b>{nombre_seguro}</b>\n💎 <b>Parte:</b> {i}/{len(clips)}\n✅ @ImperioMP_Oficial"
            
            try:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML")
                print(f"✔️ Ep {i} enviado.")
            except Exception as e:
                print(f"❌ Error en envío Ep {i}: {e}")

        if os.path.exists(path_v): os.remove(path_v)
        if os.path.exists(path_t): os.remove(path_t)
        time.sleep(2.5)

    if os.path.exists(video_path): os.remove(video_path)
    bot.send_message(config.CHAT_ID, f"🏁 <b>TEMPORADA FINALIZADA</b>", parse_mode="HTML")

# ... (Interfaz Web permanece igual) ...

@app.route('/')
def index():
    return render_template_string('''<body style="background:#000;color:#e50914;text-align:center;padding-top:100px;font-family:sans-serif;"><h1>MALLY SERIES <span style="color:#fff">PRO</span></h1><form action="/upload" method="post" enctype="multipart/form-data"><label style="background:#e50914;color:#fff;padding:15px 30px;cursor:pointer;font-weight:bold;">NUEVA PRODUCCIÓN<input type="file" name="file" accept="video/*" onchange="this.form.submit()" style="display:none;"></label></form></body>''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = "input_pro.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_pro, args=(save_path, file.filename)).start()
    return "<h1>🚀 Procesando...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
