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

# --- SISTEMA DE BASE DE DATOS ---
def actualizar_db(video_name, total_parts):
    db_path = "database.json"
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f: json.dump({"temporadas": []}, f)
    
    with open(db_path, 'r+') as f:
        db = json.load(f)
        n_temp = len(db['temporadas']) + 1
        nueva = {
            "numero": n_temp,
            "nombre": video_name,
            "total_episodios": total_parts,
            "partes": [{"num": i, "estado": "pendiente"} for i in range(1, total_parts + 1)]
        }
        db['temporadas'].append(nueva)
        f.seek(0)
        json.dump(db, f, indent=2)
        f.truncate()
    return n_temp

# --- MOTOR DE PRODUCCIÓN ---
def motor_mally_pro(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    # FFmpeg Segmentación (Hyper-Speed)
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    subprocess.run(['ffmpeg', '-i', video_path, '-f', 'segment', '-segment_time', '60', '-reset_timestamps', '1', '-c:v', 'copy', '-c:a', 'copy', output_pattern], check=True)
    
    clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
    temp_id = actualizar_db(original_name, len(clips))
    
    bot.send_message(config.CHAT_ID, f"🎬 **PRODUCCIÓN INICIADA**\nSerie: {original_name}\nEpisodios: {len(clips)}")

    for i, clip_name in enumerate(clips, 1):
        path_v = os.path.join(config.TEMP_FOLDER, clip_name)
        path_thumb = path_v.replace(".mp4", ".jpg")
        
        # Generar Miniatura
        subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_thumb], capture_output=True)

        # --- FIX: MANEJO SEGURO DE ARCHIVOS CON EXITSTACK ---
        with ExitStack() as stack:
            v = stack.enter_context(open(path_v, 'rb'))
            
            t = None
            if os.path.exists(path_thumb):
                t = stack.enter_context(open(path_thumb, 'rb'))

            caption = f"🎬 **{original_name}**\n💎 S{temp_id:02d} | E{i:03d}\n✅ @ImperioMP_Oficial"
            
            try:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="Markdown")
                print(f"✔️ Publicado: Ep {i}")
            except Exception as e:
                print(f"❌ Error enviando Ep {i}: {e}")

        # Limpieza tras cerrar archivos
        if os.path.exists(path_v): os.remove(path_v)
        if os.path.exists(path_thumb): os.remove(path_thumb)
        time.sleep(2) # Anti-Flood

    if os.path.exists(video_path): os.remove(video_path)
    bot.send_message(config.CHAT_ID, f"🏁 **TEMPORADA {temp_id} FINALIZADA**")

# --- INTERFAZ WEB ---
@app.route('/')
def index():
    return render_template_string('''
    <body style="background:#000;color:#e50914;font-family:sans-serif;text-align:center;padding-top:100px;">
        <h1>MALLY SERIES <span style="color:#fff">PRO</span></h1>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" onchange="this.form.submit()" style="display:none;" id="up">
            <label for="up" style="background:#e50914;color:#fff;padding:15px 30px;cursor:pointer;font-weight:bold;">NUEVA SERIE</label>
        </form>
    </body>
    ''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = "input_pro.mp4"
    file.save(path)
    threading.Thread(target=motor_mally_pro, args=(path, file.filename)).start()
    return "<h1>🚀 Subida exitosa. Procesando...</h1><script>setTimeout(()=>window.location='/',2000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
