import ffmpeg
import os
import sys
import telebot
from flask import Flask, render_template, jsonify, request

# --- CONFIGURACIÓN MAESTRA ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHAT_ID = "-1003584710096"
FOTO_PORTADA = "foto.jpg"
TEMP_FOLDER = "mally_studio_segments"
THUMB_FOLDER = "static/thumbs"

sys.dont_write_bytecode = True
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Asegurar infraestructura de carpetas
for folder in [TEMP_FOLDER, THUMB_FOLDER, 'templates']:
    if not os.path.exists(folder):
        os.makedirs(folder)

def generar_miniatura(video_path, thumb_path):
    """Genera el preview visual para la galería."""
    if not os.path.exists(thumb_path):
        try:
            (ffmpeg.input(video_path, ss=1)
             .filter('scale', 400, -1)
             .output(thumb_path, vframes=1)
             .run(quiet=True, overwrite_output=True))
        except: pass

def motor_sakura_v10(video_filename, serie_name):
    """Corta, inyecta portada y envía linealmente."""
    try:
        v_abs = os.path.abspath(video_filename)
        p_abs = os.path.abspath(FOTO_PORTADA)
        
        probe = ffmpeg.probe(v_abs)
        duration = float(probe['format']['duration'])
        total = int(duration // 60) + (1 if duration % 60 > 0 else 0)

        for i in range(total):
            actual = i + 1
            out_p = os.path.join(TEMP_FOLDER, f"clip_{actual}.mp4")
            
            # Procesamiento optimizado (Anti-413)
            (ffmpeg.input(v_abs, ss=i*60, t=60)
             .overlay(ffmpeg.input(p_abs), enable='between(t,0,0.05)')
             .output(out_p, vcodec='libx264', preset='ultrafast', acodec='aac',
                     video_bitrate='3.8M', maxrate='4M', bufsize='6M',
                     pix_fmt='yuv420p', map_metadata=-1, loglevel="error")
             .overwrite_output().run(quiet=True))

            # Envío con el título dinámico
            caption = f"🎬 {serie_name}\n💎 CAPÍTULO: {actual}/{total}\n🔗 @MallySeries"
            with open(out_p, 'rb') as v:
                bot.send_video(CHAT_ID, v, caption=caption, 
                               supports_streaming=True, timeout=300)
            
            if os.path.exists(out_p): os.remove(out_p)

        return f"Éxito: {serie_name} enviada completa."
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    videos_data = []
    # Escaneo de galería
    for f in os.listdir('.'):
        if f.endswith('.mp4'):
            thumb_name = f.replace('.mp4', '.jpg')
            thumb_path = os.path.join(THUMB_FOLDER, thumb_name)
            generar_miniatura(f, thumb_path)
            videos_data.append({'name': f, 'thumb': thumb_name})
    return render_template('index.html', videos=videos_data)

@app.route('/run', methods=['POST'])
def run_task():
    data = request.get_json()
    resultado = motor_sakura_v10(data.get('video_file'), data.get('serie_name'))
    return jsonify({"message": resultado})

if __name__ == '__main__':
    print("🚀 SAKURA CORE V10.2 ONLINE")
    app.run(host='0.0.0.0', port=5000)
