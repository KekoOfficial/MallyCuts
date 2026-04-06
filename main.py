import os
import subprocess
import threading
import time
from flask import Flask, render_template_string, request
from telebot import TeleBot
import config

bot = TeleBot(config.API_TOKEN)
app = Flask(__name__)

def limpiar_html(texto):
    return texto.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def enviar_y_limpiar(path_v, caption, index):
    """Envía el video y su miniatura, luego borra los temporales"""
    path_t = path_v.replace(".mp4", ".jpg")
    # Generar miniatura rápida
    subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:01', '-vframes', '1', path_t], capture_output=True)
    
    try:
        with open(path_v, 'rb') as v, open(path_t, 'rb') as t:
            bot.send_video(config.CHAT_ID, v, thumb=t, caption=caption, parse_mode="HTML")
        print(f"✅ Parte {index} enviada con éxito.")
    except Exception as e:
        print(f"❌ Error en envío parte {index}: {e}")
    finally:
        if os.path.exists(path_v): os.remove(path_v)
        if os.path.exists(path_t): os.remove(path_t)

def motor_mally_asincrono(video_path, original_name):
    if not os.path.exists(config.TEMP_FOLDER): os.makedirs(config.TEMP_FOLDER)
    nombre_seguro = limpiar_html(original_name)

    # 1. Obtener duración total para calcular capítulos
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path], capture_output=True, text=True)
    duracion_total = float(result.stdout)
    total_capitulos = int(duracion_total // config.CLIP_DURATION) + (1 if duracion_total % config.CLIP_DURATION > 0 else 0)

    bot.send_message(config.CHAT_ID, f"🎬 <b>PRODUCCIÓN INICIADA</b>\nSerie: {nombre_seguro}\nTotal Capítulos: {total_capitulos}\n⚡ @MallySeries", parse_mode="HTML")

    # 2. Corte y Envío Secuencial (Uno por uno)
    # Usamos un bucle manual para cortar y enviar sin esperar al resto
    for i in range(total_capitulos):
        start_time = i * config.CLIP_DURATION
        output_file = os.path.join(config.TEMP_FOLDER, f"parte_{i+1:03d}.mp4")
        
        # Cortar solo el segmento actual
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(start_time), '-t', str(config.CLIP_DURATION),
            '-i', video_path, '-c', 'copy', '-avoid_negative_ts', '1', output_file
        ], check=True)

        caption = (
            f"🎬 <b>{nombre_seguro}</b>\n"
            f"💎 <b>Capítulo:</b> {i+1}/{total_capitulos}\n"
            f"✅ @MallySeries"
        )
        
        # ENVIAR INMEDIATAMENTE
        enviar_y_limpiar(output_file, caption, i+1)
        time.sleep(1) # Pequeño respiro para el sistema

    if os.path.exists(video_path): os.remove(video_path)
    bot.send_message(config.CHAT_ID, f"🏁 <b>Mally Series:</b> {nombre_seguro} finalizada.", parse_mode="HTML")

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mally Series Studio</title>
        <style>
            body { background:#000; color:#0f0; font-family:monospace; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
            .box { border: 2px solid #0f0; padding: 40px; background:rgba(0,20,0,0.9); border-radius:15px; text-align:center; box-shadow: 0 0 20px #0f0; }
            h1 { color:#f0f; text-shadow: 2px 2px #000; }
            .btn { display:inline-block; margin-top:25px; padding:15px 40px; background:#f0f; color:#fff; font-weight:bold; cursor:pointer; border-radius:8px; border:none; text-transform:uppercase; box-shadow: 0 5px 0 #800080; }
            .btn:active { transform: translateY(3px); box-shadow: 0 2px 0 #800080; }
            input[type="file"] { display:none; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>MALLY SERIES PRO</h1>
            <p>> MODO: FLUJO ASÍNCRONO 3MIN</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <label class="btn">SELECCIONAR DE GALERÍA<input type="file" name="file" accept="video/*" onchange="this.form.submit()"></label>
            </form>
        </div>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file: return "Error", 400
    save_path = f"input_{int(time.time())}.mp4"
    file.save(save_path)
    threading.Thread(target=motor_mally_asincrono, args=(save_path, file.filename)).start()
    return "<h1>🎥 Procesando y Enviando Capítulos...</h1><script>setTimeout(()=>window.location='/', 3000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
