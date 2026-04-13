import os, subprocess, threading, time
from flask import Flask, render_template_string, request
from telebot import TeleBot, apihelper
import config, logger

# Configuración de red para evitar Timeout
apihelper.CONNECT_TIMEOUT = 600
apihelper.READ_TIMEOUT = 600
bot = TeleBot(config.API_TOKEN, threaded=False)
app = Flask(__name__)

def enviar_y_limpiar(path_v, nombre_serie, n, total, mally_log):
    path_t = path_v.replace(".mp4", ".jpg")
    subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:02', '-vframes', '1', path_t], capture_output=True)
    
    for intento in range(3):
        try:
            with open(path_v, 'rb') as v, open(path_t, 'rb') as t:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=mally_log.exito(n), parse_mode="HTML", timeout=600)
            break
        except Exception as e:
            time.sleep(5)
    
    if os.path.exists(path_v): os.remove(path_v)
    if os.path.exists(path_t): os.remove(path_t)

def motor_mally_pro(path_video, path_portada, nombre_serie, descripcion):
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # Calcular capítulos
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path_video], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre_serie, total)

    # Enviar portada
    try:
        with open(path_portada, 'rb') as p:
            bot.send_photo(config.CHAT_ID, p, caption=mally_log.portada_msg(descripcion), parse_mode="HTML")
        os.remove(path_portada)
    except: pass

    # Bucle asíncrono
    for i in range(total):
        n = i + 1
        salida = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
        subprocess.run(['ffmpeg', '-y', '-ss', str(i * config.CLIP_DURATION), '-t', str(config.CLIP_DURATION), '-i', path_video, '-c', 'copy', '-avoid_negative_ts', '1', salida], check=True)
        enviar_y_limpiar(salida, nombre_serie, n, total, mally_log)
        time.sleep(2)

    if os.path.exists(path_video): os.remove(path_video)
    bot.send_message(config.CHAT_ID, mally_log.final(), parse_mode="HTML")

@app.route('/')
def index():
    return render_template_string('''''')

@app.route('/upload', methods=['POST'])
def upload():
    nombre, desc = request.form['nombre'], request.form['descripcion']
    p_port = f"img_{time.time()}.jpg"
    p_vid = f"vid_{time.time()}.mp4"
    request.files['portada'].save(p_port)
    request.files['video'].save(p_vid)
    threading.Thread(target=motor_mally_pro, args=(p_vid, p_port, nombre, desc)).start()
    return "<h1>🕹️ Procesando Mally Series...</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
