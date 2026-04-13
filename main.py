import os, subprocess, threading, time
from flask import Flask, render_template, request
from telebot import TeleBot, apihelper
import config, logger

# Ajuste de red para Termux
apihelper.CONNECT_TIMEOUT = 600
bot = TeleBot(config.API_TOKEN, threaded=False)
app = Flask(__name__)

def enviar_asincrono(path_v, n, total, mally_log):
    path_t = path_v.replace(".mp4", ".jpg")
    # Generar miniatura
    subprocess.run(['ffmpeg', '-y', '-i', path_v, '-ss', '00:00:02', '-vframes', '1', path_t], capture_output=True)
    
    for _ in range(3): # Reintentos
        try:
            with open(path_v, 'rb') as v, open(path_t, 'rb') as t:
                bot.send_video(config.CHAT_ID, v, thumb=t, caption=mally_log.exito(n), parse_mode="HTML", timeout=600)
            break
        except: time.sleep(5)
    
    if os.path.exists(path_v): os.remove(path_v)
    if os.path.exists(path_t): os.remove(path_t)

def motor_cerebro(p_vid, p_port, nombre, desc):
    os.makedirs(config.TEMP_FOLDER, exist_ok=True)
    
    # Calcular duración y partes
    res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', p_vid], capture_output=True, text=True)
    total = int(float(res.stdout) // config.CLIP_DURATION) + 1
    mally_log = logger.MallyLogger(nombre, total)

    # 1. Enviar Portada
    try:
        with open(p_port, 'rb') as img:
            bot.send_photo(config.CHAT_ID, img, caption=mally_log.portada_msg(desc), parse_mode="HTML")
        os.remove(p_port)
    except Exception as e: print(f"Error Portada: {e}")

    # 2. Bucle: Corta 1 -> Envía 1
    for i in range(total):
        n = i + 1
        salida = os.path.join(config.TEMP_FOLDER, f"cap_{n:03d}.mp4")
        
        # Corte rápido con Stream Copy
        subprocess.run(['ffmpeg', '-y', '-ss', str(i*config.CLIP_DURATION), '-t', str(config.CLIP_DURATION), '-i', p_vid, '-c', 'copy', '-avoid_negative_ts', '1', salida], check=True)
        
        # Envío inmediato (mientras se corta el siguiente)
        enviar_asincrono(salida, n, total, mally_log)
        time.sleep(1)

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
    
    threading.Thread(target=motor_cerebro, args=(p_vid, p_port, n, d)).start()
    return "<h1>🕹️ PRODUCCIÓN INICIADA</h1><script>setTimeout(()=>window.location='/', 3000)</script>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
