import os
import subprocess
import threading
from flask import Flask, render_template_string, request, redirect
from telebot import TeleBot
import config

# Inicialización
bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

# Asegurar directorios
if not os.path.exists(config.TEMP_FOLDER):
    os.makedirs(config.TEMP_FOLDER)

def motor_de_corte(video_path):
    """Segmentación ultra-rápida sin recodificar"""
    bot.send_message(config.CHAT_ID, "🚀 **Motor Iniciado**: Procesando video...")
    
    output_pattern = os.path.join(config.TEMP_FOLDER, "part_%03d.mp4")
    
    # Comando FFmpeg -c copy (Velocidad instantánea)
    comando = [
        'ffmpeg', '-i', video_path,
        '-f', 'segment',
        '-segment_time', str(config.CLIP_DURATION),
        '-reset_timestamps', '1',
        '-c', 'copy', 
        output_pattern
    ]

    try:
        subprocess.run(comando, check=True, capture_output=True)
        
        # Enviar clips ordenados
        clips = sorted([f for f in os.listdir(config.TEMP_FOLDER) if f.startswith('part_')])
        
        for clip in clips:
            path_clip = os.path.join(config.TEMP_FOLDER, clip)
            with open(path_clip, 'rb') as v:
                bot.send_video(config.CHAT_ID, v, caption=f"🎬 Clip: {clip}")
            os.remove(path_clip) # Limpieza inmediata
            
        bot.send_message(config.CHAT_ID, "✅ **Proceso Finalizado**: Clips enviados a Telegram.")
    except Exception as e:
        bot.send_message(config.CHAT_ID, f"❌ **Error en Motor**: {e}")
    finally:
        if os.path.exists(video_path): os.remove(video_path)

@app.route('/')
def index():
    # El HTML está integrado aquí para que sea un solo archivo main
    return render_template_string(HTML_INTERFACE)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files: return redirect('/')
    file = request.files['file']
    if file.filename == '': return redirect('/')
    
    temp_input = "input_upload.mp4"
    file.save(temp_input)
    
    # Ejecutar motor en segundo plano para no congelar Chrome
    threading.Thread(target=motor_de_corte, args=(temp_input,)).start()
    return "<h1>🚀 Procesando... Mira tu Telegram.</h1><script>setTimeout(()=>window.location='/', 3000)</script>"

# Interfaz Cyber-Imperial
HTML_INTERFACE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chrome Magic Good V2</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #00ff41; font-family: 'Courier New', monospace; margin: 0; display: flex; align-items: center; justify-content: center; height: 100vh; }
        .console { border: 2px solid #00ff41; padding: 30px; box-shadow: 0 0 20px #00ff41; border-radius: 15px; text-align: center; background: rgba(0,255,65,0.05); }
        h1 { text-shadow: 0 0 10px #00ff41; letter-spacing: 2px; }
        .status { color: #ff00ff; font-weight: bold; margin: 15px 0; }
        .upload-area { margin-top: 25px; border: 1px dashed #00ff41; padding: 20px; position: relative; }
        input[type="file"] { position: absolute; width: 100%; height: 100%; top: 0; left: 0; opacity: 0; cursor: pointer; }
        .btn { background: #00ff41; color: #000; padding: 10px 20px; border: none; font-weight: bold; cursor: pointer; }
        .info { font-size: 0.7rem; color: #555; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="console">
        <h1>[ CHROME MAGIC V2 ]</h1>
        <div class="status">> MOTOR: LISTO PARA SUBIDA</div>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <div class="upload-area">
                <p>SELECCIONAR VIDEO</p>
                <input type="file" name="file" accept="video/*" onchange="this.form.submit()">
            </div>
        </form>
        <div class="info">Auto-Corte: 60s | Engine: FFmpeg-Copy | By Noa</div>
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    print(f"💎 Servidor en: http://0.0.0.0:{config.PORT}")
    app.run(host='0.0.0.0', port=config.PORT, debug=False)
