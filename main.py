import os, subprocess, time, threading
from flask import Flask, render_template, request
from telebot import TeleBot, apihelper
import config, logger

apihelper.CONNECT_TIMEOUT = 600
bot = TeleBot(config.API_TOKEN, threaded=False)
app = Flask(__name__)

def procesar_y_enviar_bloque(path_original, n, total, mally_log):
    """Corta, edita y envía un solo bloque de 60s"""
    inicio = (n - 1) * config.CLIP_DURATION
    segmento_raw = os.path.join(config.TEMP_FOLDER, f"raw_{n}.mp4")
    segmento_final = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
    path_thumb = segmento_final.replace(".mp4", ".jpg")

    try:
        # 1. Corte rápido del segmento original (60s)
        subprocess.run([
            'ffmpeg', '-y', '-ss', str(inicio), '-t', str(config.CLIP_DURATION),
            '-i', path_original, '-c', 'copy', '-avoid_negative_ts', '1', segmento_raw
        ], check=True, capture_output=True)

        # 2. Edición: Aplicar marca de agua SOLO a ese minuto (Muy rápido)
        subprocess.run([
            'ffmpeg', '-y', '-i', segmento_raw,
            '-vf', f"drawtext=text='{config.WATERMARK_TEXT}':x=w-tw-20:y=h-th-20:fontcolor={config.WATERMARK_COLOR}:fontsize=24",
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28', '-c:a', 'copy', segmento_final
        ], check=True, capture_output=True)

        # 3. Generar Miniatura
        subprocess.run(['ffmpeg', '-y', '-i', segmento_final, '-ss', '00:00:01', '-vframes', '1', path_thumb], capture_output=True)

        # 4. Envío Sincronizado (Garantiza el Orden)
        with open(segmento_final, 'rb') as v, open(path_thumb, 'rb') as t:
            bot.send_video(config.CHAT_ID, v, thumb=t, caption=mally_log.exito(n), parse_mode="HTML", timeout=600)
        
        print(f"✅ {mally_log.cortando(n)} - Enviado con éxito.")

    except Exception as e:
        print(f"❌ Error en capítulo {n}: {e}")
    finally:
        # Limpieza de archivos temporales de este bloque
        for f in [segmento_raw, segmento_final, path_thumb]:
            if os.path.exists(f): os.remove(f)

def motor_mally_cascada(p_vid, p_port, nombre, desc):
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # Info del video
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total)

    # Enviar Portada Primero
    try:
        with open(p_port, 'rb') as img:
            bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
        os.remove(p_port)
    except: pass

    # PROCESAMIENTO EN ORDEN
    for n in range(1, total + 1):
        procesar_y_enviar_bloque(p_vid, n, total, mally_log)
        # Pequeña pausa para que Telegram no sature el orden
        time.sleep(2)

    if os.path.exists(p_vid): os.remove(p_vid)
    bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")

@app.route('/')
def index(): return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    n, d = request.form['nombre'], request.form['descripcion']
    p_port, p_vid = f"p_{time.time()}.jpg", f"v_{time.time()}.mp4"
    request.files['portada'].save(p_port)
    request.files['video'].save(p_vid)
    threading.Thread(target=motor_mally_cascada, args=(p_vid, p_port, n, d)).start()
    return "<h1>🕹️ PRODUCCIÓN EN CASCADA INICIADA</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
