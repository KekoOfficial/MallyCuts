import os
import subprocess
import threading
import time
from flask import Flask, render_template_string, request
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

def generar_thumbnail(video_path, output_thumb):
    """Extrae un frame del segundo 2 para usar de portada"""
    comando = [
        'ffmpeg', '-y', '-i', video_path,
        '-ss', '00:00:02', '-vframes', '1',
        output_thumb
    ]
    subprocess.run(comando, capture_output=True)

def motor_netflix(video_path):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    
    bot.send_message(config.CHANNEL_ID, f"🎬 **Mally Series**: Iniciando Temporada {config.TEMPORADA}...")

    # Corte Ultra-Rápido
    output_pattern = os.path.join(config.TEMP_FOLDER, "ep_%03d.mp4")
    subprocess.run([
        'ffmpeg', '-i', video_path, '-f', 'segment',
        '-segment_time', str(config.CLIP_DURATION),
        '-reset_timestamps', '1', '-c', 'copy', output_pattern
    ], check=True)

    episodios = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('ep_')])
    
    for i, ep in enumerate(episodios, 1):
        path_video = os.path.join(config.TEMP_FOLDER, ep)
        path_thumb = path_video.replace(".mp4", ".jpg")
        
        # Crear miniatura para que se vea como Netflix
        generar_thumbnail(path_video, path_thumb)
        
        caption = f"🎬 **Mally Series**\n📌 Temporada {config.TEMPORADA} | Episodio {i}\n💎 @ImperioMP_Oficial"
        
        with open(path_video, 'rb') as v, open(path_thumb, 'rb') as t:
            bot.send_video(config.CHANNEL_ID, v, thumb=t, caption=caption, parse_mode="Markdown")
        
        # Limpieza y Delay anti-flood
        os.remove(path_video)
        os.remove(path_thumb)
        time.sleep(3) # Pausa de seguridad de 3 segundos

    bot.send_message(config.CHANNEL_ID, f"✅ **Temporada {config.TEMPORADA} completa.**")
    if os.path.exists(video_path): os.remove(video_path)

@app.route('/')
def index():
    return render_template_string(HTML_CONSOLE)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    path = "raw_video.mp4"
    file.save(path)
    threading.Thread(target=motor_netflix, args=(path,)).start()
    return "<h1>🎥 Producción Iniciada. Revisa el Canal.</h1><script>setTimeout(()=>window.location='/', 2000)</script>"

HTML_CONSOLE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mally Series Studio</title>
    <style>
        body { background: #000; color: #e50914; font-family: 'Arial', sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .card { border: 2px solid #e50914; padding: 40px; box-shadow: 0 0 30px rgba(229, 9, 20, 0.5); text-align: center; background: #141414; border-radius: 10px; }
        .btn { background: #e50914; color: white; padding: 15px 30px; border: none; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 20px; }
        input[type="file"] { display: none; }
    </style>
</head>
<body>
    <div class="card">
        <h1 style="color: white; margin-bottom: 5px;">MALLY <span style="color: #e50914;">SERIES</span></h1>
        <p style="color: #808080;">SISTEMA DE PRODUCCIÓN AUTOMÁTICA</p>
        <hr style="border: 0.5px solid #333;">
        <form action="/upload" method="post" enctype="multipart/form-data">
            <label class="btn">
                SUBIR TEMPORADA
                <input type="file" name="file" accept="video/*" onchange="this.form.submit()">
            </label>
        </form>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=config.PORT)
