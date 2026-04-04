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
    """Evita errores de parseo en Telegram"""
    return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def gestionar_db(video_name, total_parts):
    db_path = "database.json"
    if not os.path.exists(db_path):
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump({"nombre": "Mally Series", "temporadas": []}, f)
    
    with open(db_path, 'r+', encoding='utf-8') as f:
        db = json.load(f)
        n_temp = len(db['temporadas']) + 1
        nueva = {
            "numero": n_temp,
            "nombre": video_name,
            "episodios": total_parts,
            "partes": [{"num": i, "estado": "pendiente"} for i in range(1, total_parts + 1)]
        }
        db['temporadas'].append(nueva)
        f.seek(0)
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.truncate()
    return n_temp

# --- MOTOR DE PRODUCCIÓN ---
def motor_mally_pro(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    nombre_seguro = limpiar_html(original_name)
    
    # 1. FFmpeg Segmentación (Stream Copy para 93x de velocidad)
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    subprocess.run([
        'ffmpeg', '-y', '-i', video_path, 
        '-f', 'segment', '-segment_time', str(config.CLIP_DURATION),
        '-reset_timestamps', '1', '-c', 'copy', output_pattern
    ], check=True)
    
    clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
    temp_id = gestionar_db(original_name, len(clips))
    
    bot.send_message(config.CHAT_ID, f"🎬 <b>PRODUCCIÓN INICIADA</b>\n<b>Serie:</b> {nombre_seguro}\n<b>Episodios:</b> {len(clips)}", parse_mode="HTML")

    # 2. Ciclo de Envío con ExitStack
    for i, clip_name in enumerate(clips, 1):
        path_v = os.path.join(config.TEMP_FOLDER, clip_name)
        path_t = path_v.replace(".mp4", ".jpg")
        
        # Extraer miniatura (Thumbnail)
        subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)

        with ExitStack() as stack:
            # Apertura segura de archivos
            v = stack.enter_context(open(path_v, 'rb'))
            t = stack.enter_context(open(path_t, 'rb')) if os.path.exists(path_t) else None

            caption = (
                f"🎬 <b>{nombre_seguro}</b>\n"
                f"💎 <b>S{temp_id:02d} | E{i:03d}</b>\n"
                f"✅ @ImperioMP_Oficial"
            )
            
            try:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML")
                print(f"✔️ Episodio {i} publicado.")
            except Exception as e:
                print(f"❌ Fallo en Ep {i}: {e}")

        # Limpieza inmediata post-envío
        if os.path.exists(path_v): os.remove(path_v)
        if os.path.exists(path_t): os.remove(path_t)
        time.sleep(2.5) # Delay para evitar Flood en series largas

    if os.path.exists(video_path): os.remove(video_path)
    bot.send_message(config.CHAT_ID, f"🏁 <b>TEMPORADA {temp_id} FINALIZADA</b>\nTotal: {len(clips)} episodios.", parse_mode="HTML")

# --- INTERFAZ WEB NETFLIX ---
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mally Series Studio</title>
        <style>
            body { background:#000; color:#fff; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
            .box { border: 1px solid #e50914; padding: 40px; background:#141414; border-radius:10px; text-align:center; box-shadow: 0 0 20px #e50914; }
            h1 { color:#e50914; letter-spacing:2px; margin:0; }
            .btn { display:inline-block; margin-top:25px; padding:12px 30px; background:#e50914; color:#fff; font-weight:bold; cursor:pointer; border-radius:5px; text-transform:uppercase; }
            input[type="file"] { display:none; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>MALLY SERIES <span style="color:#fff">PRO</span></h1>
            <p style="color:#555;">SISTEMA AUTOMATIZADO MP</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label class="btn">NUEVA PRODUCCIÓN<input type="file" name="file" accept="video/*" onchange="this.form.submit()"></label>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file: return "Error", 400
    save_path = "input_pro.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_pro, args=(save_path, file.filename)).start()
    return "<h1>🎥 Producción en curso...</h1><script>setTimeout(()=>window.location='/', 2500)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
