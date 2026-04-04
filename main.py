import os, subprocess, threading, time, json
from flask import Flask, render_template_string, request
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# --- GESTIÓN DE BASE DE DATOS ---
def gestionar_db(video_name, total_parts):
    db_path = "database.json"
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    nueva_temp = {
        "numero": len(db['temporadas']) + 1,
        "nombre": f"Temporada {len(db['temporadas']) + 1} - {video_name}",
        "partes": []
    }
    
    for i in range(1, total_parts + 1):
        nueva_temp['partes'].append({
            "numero": i,
            "titulo": f"Parte {i}",
            "duracion": "60s",
            "estado": "pendiente"
        })
    
    db['temporadas'].append(nueva_temp)
    with open(db_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    return nueva_temp['numero']

def marcar_publicado(temp_num, parte_num):
    with open("database.json", 'r+', encoding='utf-8') as f:
        db = json.load(f)
        for t in db['temporadas']:
            if t['numero'] == temp_num:
                t['partes'][parte_num-1]['estado'] = "publicado"
        f.seek(0)
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.truncate()

# --- MOTOR DE PROCESAMIENTO ---
def procesar_mally_series(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    # 1. Corte Ultra-Rápido
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    subprocess.run(['ffmpeg', '-i', video_path, '-f', 'segment', '-segment_time', '60', '-reset_timestamps', '1', '-c', 'copy', output_pattern])
    
    clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
    
    # 2. Registrar en JSON
    temp_activa = gestionar_db(original_name, len(clips))
    bot.send_message(config.CHAT_ID, f"🎬 **Mally Series**: {original_name}\n🚀 Registrando Temporada {temp_activa}...")

    # 3. Envío y Portadas
    for i, clip in enumerate(clips, 1):
        path_v = os.path.join(config.TEMP_FOLDER, clip)
        path_t = path_v.replace(".mp4", ".jpg")
        
        # Generar miniatura rápida
        subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)
        
        caption = f"🎬 **{original_name}**\n💎 Temporada {temp_activa} | Episodio {i}\n✅ Estado: Publicado"
        
        with open(path_v, 'rb') as v, open(path_thumb, 'rb') if os.path.exists(path_t) else None as t:
            bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="Markdown")
        
        marcar_publicado(temp_activa, i)
        os.remove(path_v)
        if os.path.exists(path_t): os.remove(path_t)
        time.sleep(3) # Anti-Flood

    if os.path.exists(video_path): os.remove(video_path)

# --- INTERFAZ Y RUTAS ---
@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    save_path = "input_video.mp4"
    file.save(save_path)
    threading.Thread(target=procesar_mally_series, args=(save_path, file.filename)).start()
    return "<h1>🎥 Producción en curso... Mira tu Telegram.</h1><script>setTimeout(()=>window.location='/', 3000)</script>"

HTML_UI = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mally Series Studio</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #fff; font-family: 'Helvetica', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .container { text-align: center; border: 1px solid #333; padding: 50px; background: #141414; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #e50914; font-size: 2.5rem; margin: 0; }
        .upload-btn { display: inline-block; margin-top: 25px; padding: 15px 35px; background: #e50914; color: #fff; font-weight: bold; cursor: pointer; text-decoration: none; border-radius: 4px; }
        input[type="file"] { display: none; }
        p { color: #808080; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MALLY SERIES</h1>
        <p>AI STUDIO & AUTOMATION</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label class="upload-btn">
                NUEVA PRODUCCIÓN
                <input type="file" name="file" accept="video/*" onchange="this.form.submit()">
            </label>
        </form>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
